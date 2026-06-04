import asyncio
import json
import time

import pytest
from httpx import ASGITransport, AsyncClient

from backend.src.main import app
from backend.src.db.session import init_db, close_db, get_session, get_run_by_id, get_steps_for_run
from backend.src.services.llm import MockLLM
from backend.src.services.tool_registry import create_default_registry
from backend.src.services.agent_loop import run_agent_loop


@pytest.fixture(autouse=True)
async def clean_db():
    """Use in-memory DB for each test."""
    from backend.src.db.session import engine, async_session as _as
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    from backend.src.db.session import Base

    # We need to reset the module-level engine to use in-memory
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


from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_full_run_success():
    """Test a complete successful run with mock LLM."""
    import tempfile
    import os

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
            {"type": "final_answer", "answer": "Test complete.", "cost": 0.005},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(scenario, f)
        scenario_path = f.name

    try:
        registry = create_default_registry()
        llm = MockLLM(scenario_path)

        async with get_session() as session:
            from backend.src.db.session import create_run

            run = await create_run(session, "Test goal", max_steps=10, max_cost_usd=1.0)
            run_id = run.id

        await run_agent_loop(run_id, "Test goal", 10, 1.0, registry, llm)

        await asyncio.sleep(0.1)

        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            assert run is not None
            assert run.status == "succeeded"
            assert run.reason == "succeeded"

            steps = await get_steps_for_run(session, run_id)
            assert len(steps) == 2
            assert steps[0].tool_name == "search_docs"
            assert steps[1].tool_name is None  # final answer
    finally:
        os.unlink(scenario_path)


@pytest.mark.asyncio
async def test_full_run_step_cap():
    """Test that step cap terminates the run."""
    import tempfile
    import os

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_web", "arguments": {"query": "test"}, "cost": 0.01},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(scenario, f)
        scenario_path = f.name

    try:
        registry = create_default_registry()
        llm = MockLLM(scenario_path)

        async with get_session() as session:
            from backend.src.db.session import create_run

            run = await create_run(session, "Test goal", max_steps=1, max_cost_usd=1.0)
            run_id = run.id

        await run_agent_loop(run_id, "Test goal", 1, 1.0, registry, llm)

        await asyncio.sleep(0.1)

        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            assert run is not None
            assert run.status == "failed"
            assert run.reason == "step_cap"
    finally:
        os.unlink(scenario_path)


@pytest.mark.asyncio
async def test_full_run_cost_cap():
    """Test that cost cap terminates the run."""
    import tempfile
    import os

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.06},
            {"type": "tool_call", "tool_name": "search_web", "arguments": {"query": "test"}, "cost": 0.06},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(scenario, f)
        scenario_path = f.name

    try:
        registry = create_default_registry()
        llm = MockLLM(scenario_path)

        async with get_session() as session:
            from backend.src.db.session import create_run

            run = await create_run(session, "Test goal", max_steps=10, max_cost_usd=0.05)
            run_id = run.id

        await run_agent_loop(run_id, "Test goal", 10, 0.05, registry, llm)

        await asyncio.sleep(0.1)

        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            assert run is not None
            assert run.status == "failed"
            assert run.reason == "cost_cap"
    finally:
        os.unlink(scenario_path)


@pytest.mark.asyncio
async def test_full_run_stuck():
    """Test that stuck detection terminates the run."""
    import tempfile
    import os

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(scenario, f)
        scenario_path = f.name

    try:
        registry = create_default_registry()
        llm = MockLLM(scenario_path)

        async with get_session() as session:
            from backend.src.db.session import create_run

            run = await create_run(session, "Test goal", max_steps=10, max_cost_usd=1.0)
            run_id = run.id

        await run_agent_loop(run_id, "Test goal", 10, 1.0, registry, llm)

        await asyncio.sleep(0.1)

        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            assert run is not None
            assert run.status == "failed"
            assert run.reason == "stuck"
    finally:
        os.unlink(scenario_path)
