import asyncio
import json
import os
import tempfile

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.src.db.session import Base, get_run_by_id, get_session, get_steps_for_run
from backend.src.services.llm import MockLLM
from backend.src.services.tool_registry import create_default_registry
from backend.src.services.agent_loop import run_agent_loop


@pytest.fixture(autouse=True)
async def clean_db():
    """Use in-memory DB for each test (same pattern as test_full_run.py)."""
    import backend.src.db.session as session_module

    original_engine = session_module.engine

    # Import both models so SQLAlchemy can resolve Run->Step relationships
    from backend.src.models.run import Run  # noqa: F401
    from backend.src.models.step import Step  # noqa: F401

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_module.engine = test_engine
    session_module.async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    yield

    session_module.engine = original_engine
    session_module.async_session = None
    await test_engine.dispose()


def _make_scenario_file(num_tool_calls: int = 1) -> str:
    """Create a temporary scenario file with the given number of tool calls followed by a final answer."""
    responses = []
    for i in range(num_tool_calls):
        responses.append(
            {
                "type": "tool_call",
                "tool_name": "search_docs",
                "arguments": {"query": f"query_{i}"},
                "cost": 0.01,
            }
        )
    responses.append(
        {
            "type": "final_answer",
            "answer": "Done.",
            "cost": 0.005,
        }
    )
    scenario = {"responses": responses}
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(scenario, f)
    return path


@pytest.mark.asyncio
async def test_concurrent_runs():
    """SC-004: 100 concurrent runs without data corruption.

    Spawns 100 concurrent agent loops and verifies:
    - All 100 runs reach a valid terminal state (succeeded or failed)
    - No duplicate step numbers within any run
    - No corrupted data (each run has the expected number of steps)
    - Total run count is exactly 100
    """
    num_runs = 100
    scenario_files = []
    run_ids = []

    try:
        # Pre-create 100 scenario files (each with 1 tool call + final answer)
        for _ in range(num_runs):
            scenario_files.append(_make_scenario_file(num_tool_calls=1))

        # Create 100 runs in the database
        async with get_session() as session:
            from backend.src.db.session import create_run

            for i in range(num_runs):
                run = await create_run(
                    session,
                    f"Concurrent goal {i}",
                    max_steps=10,
                    max_cost_usd=1.0,
                )
                run_ids.append(run.id)

        # Spawn 100 concurrent agent loop calls
        tasks = []
        for i, run_id in enumerate(run_ids):
            registry = create_default_registry()
            llm = MockLLM(scenario_files[i])
            tasks.append(
                run_agent_loop(
                    run_id,
                    f"Concurrent goal {i}",
                    max_steps=10,
                    max_cost_usd=1.0,
                    registry=registry,
                    llm=llm,
                )
            )

        await asyncio.gather(*tasks)

        # Allow a brief moment for any pending writes
        await asyncio.sleep(0.1)

        # Verify all 100 runs
        async with get_session() as session:
            # Check total run count
            from sqlalchemy import func, select
            from backend.src.models.run import Run

            count_result = await session.execute(select(func.count()).select_from(Run))
            total_count = count_result.scalar()
            assert total_count == num_runs, f"Expected {num_runs} runs, got {total_count}"

            for run_id in run_ids:
                run = await get_run_by_id(session, run_id)
                assert run is not None, f"Run {run_id} not found"

                # Each run must be in a terminal state
                assert run.status in ("succeeded", "failed"), f"Run {run_id} has non-terminal status: {run.status}"
                assert run.reason is not None, f"Run {run_id} has no termination reason"

                # Retrieve steps for this run
                steps = await get_steps_for_run(session, run_id)

                # Each run should have exactly 2 steps (1 tool call + 1 final answer)
                assert len(steps) == 2, f"Run {run_id} has {len(steps)} steps, expected 2"

                # Check no duplicate step numbers within this run
                step_numbers = [s.step_number for s in steps]
                assert len(step_numbers) == len(set(step_numbers)), (
                    f"Run {run_id} has duplicate step numbers: {step_numbers}"
                )

                # Verify step numbers are sequential starting from 1
                assert step_numbers == sorted(step_numbers), (
                    f"Run {run_id} has non-sequential step numbers: {step_numbers}"
                )

    finally:
        # Clean up temporary scenario files
        for path in scenario_files:
            try:
                os.unlink(path)
            except OSError:
                pass
