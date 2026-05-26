from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PushHistory(BaseModel):
    __tablename__ = "push_history"

    rule_id: Mapped[int | None] = mapped_column(ForeignKey("linkage_rule.id"), nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    event_type_id: Mapped[int | None] = mapped_column(ForeignKey("event_type.id"), nullable=True)
    push_channels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    push_target: Mapped[str | None] = mapped_column(String(200), nullable=True)
    push_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    operator: Mapped[str | None] = mapped_column(String(50), nullable=True)
    count: Mapped[int] = mapped_column(default=1)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_push_history_rule", "rule_id"),
        Index("idx_push_history_device", "device_id"),
        Index("idx_push_history_time", "push_time"),
        Index("idx_push_history_status", "status"),
    )