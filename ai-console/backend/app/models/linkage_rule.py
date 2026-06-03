from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class LinkageRule(BaseModel):
    __tablename__ = "linkage_rule"

    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_mode: Mapped[str] = mapped_column(String(20), default="AUTO", nullable=False)
    algorithm_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm.id"), nullable=True)
    event_type_id: Mapped[int | None] = mapped_column(ForeignKey("event_type.id"), nullable=True)
    level: Mapped[int] = mapped_column(default=1)
    delay_push: Mapped[int] = mapped_column(default=0)
    is_compliant: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_level: Mapped[int] = mapped_column(default=1)
    send_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delay_value: Mapped[int | None] = mapped_column(nullable=True)
    delay_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    push_channels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    app_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    app_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    template_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wechat_app_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wechat_app_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wechat_template_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sms_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    push_target: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_linkage_algorithm", "algorithm_id"),
        Index("idx_linkage_event_type", "event_type_id"),
        Index("idx_linkage_trigger_mode", "trigger_mode"),
        Index("idx_linkage_status", "status"),
    )