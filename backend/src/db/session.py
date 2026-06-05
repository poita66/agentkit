from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global engine
    if engine is None:
        engine = create_async_engine(
            "sqlite+aiosqlite:///./agent_loop.db",
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global async_session
    if async_session is None:
        async_session = async_sessionmaker(get_engine(), expire_on_commit=False)
    return async_session


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables. Safe to call multiple times."""
    from backend.src.models.run import Run  # noqa: F401
    from backend.src.models.step import Step  # noqa: F401

    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close the engine connection pool."""
    global engine, async_session
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session = None


async def get_run_by_id(session: AsyncSession, run_id: str):
    from backend.src.models.run import Run

    return await session.get(Run, run_id)


async def create_run(session: AsyncSession, goal: str, max_steps: int = 20, max_cost_usd: float = 0.5):
    from backend.src.models.run import Run

    run = Run(
        goal=goal,
        max_steps=max_steps,
        max_cost_usd=max_cost_usd,
        status="running",
        started_at=datetime.now(UTC),
    )
    session.add(run)
    await session.flush()
    return run


async def update_run_terminal(session: AsyncSession, run_id: str, reason: str):
    from backend.src.models.run import Run

    run = await session.get(Run, run_id)
    if run:
        run.status = "succeeded" if reason == "succeeded" else "failed"
        run.reason = reason
        run.finished_at = datetime.now(UTC)
        await session.flush()


async def create_step(
    session: AsyncSession,
    run_id: str,
    step_number: int,
    tool_name: str | None,
    args_json: str | None,
    result_json: str,
    cost: float,
):
    from backend.src.models.step import Step

    step = Step(
        run_id=run_id,
        step_number=step_number,
        tool_name=tool_name,
        args_json=args_json,
        result_json=result_json,
        cost=cost,
        created_at=datetime.now(UTC),
    )
    session.add(step)
    await session.flush()
    return step


async def get_steps_for_run(session: AsyncSession, run_id: str):
    from sqlalchemy import select

    from backend.src.models.step import Step

    result = await session.execute(select(Step).where(Step.run_id == run_id).order_by(Step.step_number))
    return result.scalars().all()


async def update_run_cost(session: AsyncSession, run_id: str, additional_cost: float):
    from backend.src.models.run import Run

    run = await session.get(Run, run_id)
    if run:
        run.total_cost += additional_cost
        await session.flush()
