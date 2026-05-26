from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class WarningEvent(BaseModel):
    __tablename__ = "warning_event"

    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organization.id"), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)
    algorithm_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm.id"), nullable=True)
    event_type_id: Mapped[int | None] = mapped_column(ForeignKey("event_type.id"), nullable=True)
    rule_id: Mapped[int | None] = mapped_column(ForeignKey("linkage_rule.id"), nullable=True)
    event_detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    process_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    is_compliant: Mapped[bool | None] = mapped_column(nullable=True)
    report_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_warning_device", "device_id"),
        Index("idx_warning_org", "org_id"),
        Index("idx_warning_region", "region_id"),
        Index("idx_warning_event_type", "event_type_id"),
        Index("idx_warning_rule", "rule_id"),
        Index("idx_warning_report_time", "report_time"),
        Index("idx_warning_process_status", "process_status"),
    )