from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Task(BaseModel):
    __tablename__ = "task"

    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), default="cron", nullable=False)
    trigger_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    algorithm_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    last_run_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_task_algorithm", "algorithm_id"),
        Index("idx_task_status", "status"),
    )