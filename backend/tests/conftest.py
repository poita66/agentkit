import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.db.session import Base


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session():
    """Create an in-memory database session for testing."""

    # Use in-memory DB for tests
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        yield session
        await session.rollback()

    await test_engine.dispose()


@pytest.fixture
def mock_llm(tmp_path):
    """Create a mock LLM with a simple scenario."""
    scenario = {
        "responses": [
            {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": "test"}, "cost": 0.01},
            {"type": "final_answer", "answer": "Test complete.", "cost": 0.005},
        ]
    }
    scenario_file = tmp_path / "test_scenario.json"
    scenario_file.write_text(__import__("json").dumps(scenario))
    from backend.src.services.llm import MockLLM

    return MockLLM(str(scenario_file))


@pytest.fixture
def tool_registry():
    from backend.src.services.tool_registry import create_default_registry

    return create_default_registry()


@pytest.fixture
async def client():
    """Create a test client for the FastAPI app."""
    from backend.src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
