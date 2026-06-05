import asyncio
import json
import logging

from sqlalchemy.exc import OperationalError

from backend.src.db.session import create_step, get_run_by_id, get_session, update_run_cost, update_run_terminal
from backend.src.services.guards import check_cost_cap, check_error_storm, check_step_cap, check_stuck, hash_args
from backend.src.services.llm import MockLLM
from backend.src.services.tool_registry import ToolRegistry
from backend.src.services.tool_runtime import ToolRuntime

logger = logging.getLogger(__name__)


async def _db_retry(func):
    """Retry a DB operation on SQLite locking errors."""
    for attempt in range(5):
        try:
            return await func()
        except OperationalError:
            if attempt == 4:
                raise
            await asyncio.sleep(0.01 * (2**attempt))


async def _persist_step(run_id, step_number, tool_name, args_json, result_json, cost):
    async def _do():
        async with get_session() as session:
            await create_step(session, run_id, step_number, tool_name, args_json, result_json, cost)
            await update_run_cost(session, run_id, cost)

    await _db_retry(_do)


async def _persist_final_answer(run_id, step_number, result_json, cost):
    async def _do():
        async with get_session() as session:
            await create_step(session, run_id, step_number, None, None, result_json, cost)
            await update_run_cost(session, run_id, cost)
            await update_run_terminal(session, run_id, "succeeded")

    await _db_retry(_do)


async def run_agent_loop(
    run_id: str,
    goal: str,
    max_steps: int,
    max_cost_usd: float,
    registry: ToolRegistry,
    llm: MockLLM,
):
    """Execute the agent loop for a single run.

    Steps:
    1. Select candidate tools via registry
    2. Call LLM with goal + past steps + tools
    3. Dispatch tool calls via runtime
    4. Check guards each iteration
    5. Persist steps atomically
    """
    runtime = ToolRuntime(registry)
    steps: list[dict] = []
    recent_for_stuck: list[tuple[str, str]] = []
    recent_errors: list[bool] = []
    total_cost = 0.0
    step_number = 0

    try:
        async with asyncio.timeout(60):
            while True:
                # Check guards before next step
                terminated, reason = check_step_cap(len(steps), max_steps)
                if terminated:
                    assert reason is not None
                    await _finalize_run(run_id, reason)
                    return

                terminated, reason = check_cost_cap(total_cost, max_cost_usd)
                if terminated:
                    assert reason is not None
                    await _finalize_run(run_id, reason)
                    return

                # Select candidate tools
                candidate_tools = registry.retrieve(goal)
                tools_dict = [
                    {"name": t.name, "description": t.description, "parameters": t.parameters} for t in candidate_tools
                ]

                # Call LLM
                response = await llm.call(goal, steps, tools_dict)

                if response.get("type") == "final_answer":
                    step_number += 1
                    answer = response.get("answer", "")
                    cost = response.get("cost", 0.0)
                    total_cost += cost

                    result_json = json.dumps({"answer": answer})
                    await _persist_final_answer(run_id, step_number, result_json, cost)

                    steps.append({"step_number": step_number, "tool_name": None, "result": result_json})
                    logger.info("Run %s completed successfully with answer: %s", run_id, answer[:100])
                    return

                # Tool call
                tool_name = response.get("tool_name")
                assert tool_name is not None
                arguments = response.get("arguments", {})
                cost = response.get("cost", 0.0)

                # Check stuck detection
                args_hash = hash_args(arguments)
                recent_for_stuck.append((tool_name, args_hash))
                terminated, reason = check_stuck(recent_for_stuck)
                if terminated:
                    assert reason is not None
                    await _finalize_run(run_id, reason)
                    return

                # Execute tool
                result = await runtime.execute(tool_name, arguments)

                step_number += 1
                result_json = json.dumps(result)
                await _persist_step(run_id, step_number, tool_name, json.dumps(arguments), result_json, cost)

                total_cost += cost

                error_info = result.get("error") or {}

                # If tool returned an error, check if recoverable
                had_error = not result.get("ok", True)
                if had_error:
                    if not error_info.get("recoverable", False):
                        # Non-recoverable error (including RETRIES_EXHAUSTED) — terminate
                        logger.error(
                            "Non-recoverable error in run %s step %d: %s",
                            run_id,
                            step_number,
                            error_info.get("message"),
                        )
                        await _finalize_run(run_id, "error")
                        return

                    recent_errors.append(True)
                    terminated, reason = check_error_storm(recent_errors)
                    if terminated:
                        assert reason is not None
                        await _finalize_run(run_id, reason)
                        return
                else:
                    recent_errors.append(False)

                steps.append(
                    {
                        "step_number": step_number,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "result": result,
                    }
                )

    except TimeoutError:
        await _finalize_run(run_id, "timeout")
        logger.info("Run %s timed out after 60s", run_id)
    except Exception as e:
        await _finalize_run(run_id, "error")
        logger.error("Run %s failed with error: %s", run_id, e)


async def _finalize_run(run_id: str, reason: str):
    async def _do():
        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            if run:
                await update_run_terminal(session, run_id, reason)

    await _db_retry(_do)
