from datetime import datetime
from sqlalchemy import String, Index, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OperationLog(BaseModel):
    __tablename__ = "operation_log"

    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_operation_log_user", "username"),
        Index("idx_operation_log_module", "module"),
        Index("idx_operation_log_time", "action_time"),
    )