import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.db.session import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal: Mapped[str] = mapped_column(String(4096), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="running")
    reason: Mapped[str | None] = mapped_column(String(16), nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    max_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    steps = relationship("Step", back_populates="run", cascade="all, delete-orphan", order_by="Step.step_number")
