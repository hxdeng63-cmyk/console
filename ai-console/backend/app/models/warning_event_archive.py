from datetime import datetime
from sqlalchemy import String, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class WarningEventArchive(BaseModel):
    __tablename__ = "warning_event_archive"

    device_id: Mapped[int | None] = mapped_column(nullable=True)
    org_id: Mapped[int | None] = mapped_column(nullable=True)
    region_id: Mapped[int | None] = mapped_column(nullable=True)
    algorithm_id: Mapped[int | None] = mapped_column(nullable=True)
    event_type_id: Mapped[int | None] = mapped_column(nullable=True)
    rule_id: Mapped[int | None] = mapped_column(nullable=True)
    event_detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    process_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    is_compliant: Mapped[bool | None] = mapped_column(nullable=True)
    report_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = ()