import asyncio
import json
import unittest.mock
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db.session import get_run_by_id, get_session, get_steps_for_run
from backend.src.services.agent_loop import run_agent_loop
from backend.src.services.llm import MockLLM
from backend.src.services.tool_registry import create_default_registry


class _MockTimeout:
    """Mock asyncio.timeout that fires after a short delay instead of 60s."""

    def __init__(self, _duration):
        pass

    async def __aenter__(self):
        await asyncio.sleep(0.1)
        raise TimeoutError()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False  # Don't suppress exceptions


@pytest.fixture(autouse=True)
async def clean_db():
    """Use in-memory DB for each test."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker

    # We need to reset the module-level engine to use in-memory
    import backend.src.db.session as session_module
    from backend.src.db.session import Base

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


@pytest.mark.asyncio
async def test_full_run_success():
    """Test a complete successful run with mock LLM."""
    import os
    import tempfile

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
    import os
    import tempfile

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
    import os
    import tempfile

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
    import os
    import tempfile

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


@pytest.mark.asyncio
async def test_full_run_timeout():
    """Test that wall-clock timeout (FR-008) terminates the run with reason 'timeout'."""
    import os
    import tempfile

    # Scenario with enough tool calls that would exceed the mocked timeout
    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test1"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test2"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test3"}, "cost": 0.01},
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test4"}, "cost": 0.01},
            {"type": "final_answer", "answer": "Should not reach here.", "cost": 0.005},
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

        # Patch asyncio.timeout to fire after 0.1s instead of 60s
        with unittest.mock.patch("asyncio.timeout", return_value=_MockTimeout(60)):
            await run_agent_loop(run_id, "Test goal", 10, 1.0, registry, llm)

        await asyncio.sleep(0.1)

        async with get_session() as session:
            run = await get_run_by_id(session, run_id)
            assert run is not None
            assert run.status == "failed"
            assert run.reason == "timeout"
    finally:
        os.unlink(scenario_path)


@pytest.mark.asyncio
async def test_full_run_error():
    """Test that an unhandled exception in the LLM terminates the run with error reason (FR-015)."""
    # Create a mock LLM that raises ValueError on call()
    mock_llm = MagicMock()
    mock_llm.call = MagicMock(side_effect=ValueError("Unexpected LLM error"))

    registry = create_default_registry()

    async with get_session() as session:
        from backend.src.db.session import create_run

        run = await create_run(session, "Test goal", max_steps=10, max_cost_usd=1.0)
        run_id = run.id

    await run_agent_loop(run_id, "Test goal", 10, 1.0, registry, mock_llm)

    await asyncio.sleep(0.1)

    async with get_session() as session:
        run = await get_run_by_id(session, run_id)
        assert run is not None
        assert run.status == "failed"
        assert run.reason == "error"


@pytest.mark.asyncio
async def test_full_run_tool_error_nonrecoverable():
    """Test that a non-recoverable tool error terminates the run immediately.

    Validates US4 scenario 2: non-recoverable error terminates the run.
    """
    import os
    import tempfile

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "err_nonrecover"}, "cost": 0.01},
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
            assert run.reason == "error"

            steps = await get_steps_for_run(session, run_id)
            assert len(steps) == 1
            assert steps[0].tool_name == "search_docs"
            result0 = json.loads(steps[0].result_json)
            assert result0["ok"] is False
            assert result0["error"]["code"] == "INVALID_ARGUMENT"
            assert result0["error"]["recoverable"] is False
    finally:
        os.unlink(scenario_path)


@pytest.mark.asyncio
async def test_full_run_tool_error_exhausted():
    """Test that when a tool returns a recoverable error (BAD_REQUEST),
    retries are exhausted but the error stays recoverable and the run continues.

    Validates US4 scenario 3: BAD_REQUEST remains recoverable after retries.
    """
    import os
    import tempfile

    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "err_recover"}, "cost": 0.01},
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
            result0 = json.loads(steps[0].result_json)
            assert result0["ok"] is False
            assert result0["error"]["code"] == "BAD_REQUEST"
            assert result0["error"]["recoverable"] is True
    finally:
        os.unlink(scenario_path)
