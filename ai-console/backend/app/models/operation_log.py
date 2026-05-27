from datetime import datetime
from sqlalchemy import String, Index, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OperationLog(BaseModel):
    __tablename__ = "operation_log"

    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_code: Mapped[int | None] = mapped_column(nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_operation_log_user", "username"),
        Index("idx_operation_log_description", "description"),
        Index("idx_operation_log_time", "action_time"),
    )