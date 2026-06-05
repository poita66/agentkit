import asyncio
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from backend.src.api.schemas import RunCreate, RunResponse, ScenarioInfo
from backend.src.db.session import create_run, get_run_by_id, get_session, get_steps_for_run
from backend.src.models.run import Run
from backend.src.services.agent_loop import run_agent_loop
from backend.src.services.tool_registry import create_default_registry

router = APIRouter()

registry = create_default_registry()
_agent_tasks: list = []  # Keep references to prevent GC

_SCENARIOS_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "scenarios"

# Friendly descriptions for each scenario file
_SCENARIO_DESCRIPTIONS: dict[str, str] = {
    "success": "Agent completes successfully with a final answer",
    "step_cap": "Agent hits the step limit",
    "cost_cap": "Agent hits the maximum cost budget",
    "stuck": "Agent gets stuck in a loop",
    "tool_error_recoverable": "Agent encounters a recoverable error and retries",
    "tool_error_nonrecoverable": "Agent encounters a non-recoverable error",
    "tool_error_exhausted": "Agent exhausts all retries on a tool error",
}


@router.get("/tools")
async def list_tools():
    return [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters,
        }
        for t in registry.list_tools()
    ]


@router.get("/scenarios")
async def list_scenarios():
    if not os.environ.get("AGENT_MOCK_ENABLED"):
        raise HTTPException(status_code=404, detail="Mock scenarios not available")
    if not _SCENARIOS_DIR.exists():
        return []
    scenarios = []
    for f in sorted(_SCENARIOS_DIR.glob("*.json")):
        name = f.stem
        if name == "default":
            continue
        scenarios.append(ScenarioInfo(name=name, description=_SCENARIO_DESCRIPTIONS.get(name, f.name)))
    return scenarios


def _match_scenario(goal: str) -> str | None:
    """Match goal text against scenario triggers. Returns scenario file path or None."""
    goal_lower = goal.lower()
    for f in sorted(_SCENARIOS_DIR.glob("*.json")):
        with open(f) as fh:
            data = json.load(fh)
        for trigger in data.get("triggers", []):
            if trigger.lower() in goal_lower:
                return str(f)
    return None


@router.post("", status_code=202)
async def create_run_endpoint(req: RunCreate):
    goal = req.goal.strip()
    if not goal:
        raise HTTPException(status_code=422, detail="Goal must not be empty or whitespace-only")
    if len(goal) > 4096:
        raise HTTPException(status_code=422, detail="Goal must not exceed 4096 characters")

    max_steps = req.max_steps or 20
    max_cost_usd = req.max_cost_usd or 0.5

    # Env var override takes precedence
    scenario_path = os.environ.get("AGENT_MOCK_SCENARIO")
    # Otherwise match goal against scenario triggers
    if not scenario_path and os.environ.get("AGENT_MOCK_ENABLED"):
        scenario_path = _match_scenario(goal) or str(_SCENARIOS_DIR / "default.json")
    if scenario_path:
        if not scenario_path.endswith(".json"):
            scenario_path = f"{_SCENARIOS_DIR}/{scenario_path}.json"
        with open(scenario_path) as f:
            scenario_data = json.load(f)
        scenario_caps = scenario_data.get("caps", {})
        if not req.max_steps:
            max_steps = scenario_caps.get("max_steps", max_steps)
        if not req.max_cost_usd:
            max_cost_usd = scenario_caps.get("max_cost_usd", max_cost_usd)

    async with get_session() as session:
        run = await create_run(session, goal, max_steps, max_cost_usd)

    # Spawn agent loop if a mock scenario is matched
    if scenario_path:
        from backend.src.services.llm import MockLLM

        llm = MockLLM(scenario_path)
        task = asyncio.create_task(run_agent_loop(run.id, goal, max_steps, max_cost_usd, registry, llm))
        _agent_tasks.append(task)

    return RunResponse(run_id=run.id)


@router.get("/{run_id}")
async def get_run_endpoint(run_id: str):
    async with get_session() as session:
        run = await get_run_by_id(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    async with get_session() as session:
        steps = await get_steps_for_run(session, run_id)

    return {
        "run_id": run.id,
        "goal": run.goal,
        "status": run.status,
        "reason": run.reason,
        "total_cost": run.total_cost,
        "max_steps": run.max_steps,
        "max_cost_usd": run.max_cost_usd,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "steps": [
            {
                "step_number": s.step_number,
                "tool_name": s.tool_name,
                "args": json.loads(s.args_json) if s.args_json else None,
                "result": json.loads(s.result_json),
                "cost": s.cost,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in steps
        ],
    }


@router.get("")
async def list_runs(limit: int = 20, offset: int = 0):
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 20

    async with get_session() as session:
        count_result = await session.execute(select(func.count()).select_from(Run))
        total = count_result.scalar()

        runs_result = await session.execute(select(Run).order_by(Run.started_at.desc()).limit(limit).offset(offset))
        runs = runs_result.scalars().all()

    return {
        "runs": [
            {
                "run_id": r.id,
                "goal": r.goal,
                "status": r.status,
                "reason": r.reason,
                "total_cost": r.total_cost,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
            for r in runs
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
