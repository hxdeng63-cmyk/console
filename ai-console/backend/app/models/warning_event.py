from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # Relationships
    files: Mapped[list["File"]] = relationship("File", back_populates="warning_event")
    event_type: Mapped["EventType"] = relationship("EventType", foreign_keys=[event_type_id])
    algorithm: Mapped["Algorithm"] = relationship("Algorithm", foreign_keys=[algorithm_id])
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    region: Mapped["Region"] = relationship("Region", foreign_keys=[region_id])
    device: Mapped["Device"] = relationship("Device", foreign_keys=[device_id])

    __table_args__ = (
        Index("idx_warning_device", "device_id"),
        Index("idx_warning_org", "org_id"),
        Index("idx_warning_region", "region_id"),
        Index("idx_warning_event_type", "event_type_id"),
        Index("idx_warning_rule", "rule_id"),
        Index("idx_warning_report_time", "report_time"),
        Index("idx_warning_process_status", "process_status"),
        Index("idx_warning_stats_event_type", "org_id", "region_id", "event_type_id", "report_time"),
        Index("idx_warning_stats_algo", "org_id", "region_id", "algorithm_id", "report_time"),
        Index("idx_warning_stats_trend", "org_id", "region_id", "report_time", "algorithm_id", "event_type_id"),
        Index("idx_warning_stats_report_time_coalesce", func.coalesce(report_time, BaseModel.created_at)),
    )
