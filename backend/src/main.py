import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api.runs import router as runs_router
from backend.src.db.session import close_db, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized, server starting")
    yield
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()
    await close_db()
    logger.info("Server shutting down")


app = FastAPI(title="Agent Loop API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(runs_router, prefix="/runs")
