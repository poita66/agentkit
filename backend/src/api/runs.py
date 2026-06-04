import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from backend.src.api.schemas import RunCreate, RunResponse
from backend.src.db.session import create_run, get_run_by_id, get_session, get_steps_for_run
from backend.src.models.run import Run
from backend.src.services.agent_loop import run_agent_loop
from backend.src.services.llm import MockLLM
from backend.src.services.tool_registry import create_default_registry

router = APIRouter()

registry = create_default_registry()
SCENARIOS_DIR = "tests/scenarios"


@router.post("", status_code=202)
async def create_run_endpoint(req: RunCreate):
    goal = req.goal.strip()
    if not goal:
        raise HTTPException(status_code=422, detail="Goal must not be empty or whitespace-only")
    if len(goal) > 4096:
        raise HTTPException(status_code=422, detail="Goal must not exceed 4096 characters")

    max_steps = req.max_steps or 20
    max_cost_usd = req.max_cost_usd or 0.5

    async with get_session() as session:
        run = await create_run(session, goal, max_steps, max_cost_usd)

    # Load scenario based on goal keywords for testing
    scenario_file = _select_scenario(goal, max_steps, max_cost_usd)
    llm = MockLLM(SCENARIOS_DIR + "/" + scenario_file)
    import asyncio

    asyncio.create_task(run_agent_loop(run.id, goal, max_steps, max_cost_usd, registry, llm))

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


def _select_scenario(goal: str, max_steps: int, max_cost_usd: float) -> str:
    """Select a scenario file based on request parameters for deterministic testing."""
    if max_steps <= 2:
        return "step_cap.json"
    if max_cost_usd <= 0.01:
        return "cost_cap.json"
    return "success.json"
