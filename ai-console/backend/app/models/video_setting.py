from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class VideoSetting(BaseModel):
    __tablename__ = "video_setting"

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)
    event_types: Mapped[dict | None] = mapped_column(JSONB, default=list, nullable=True)
    record_duration_seconds: Mapped[int] = mapped_column(default=10)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        Index("idx_video_setting_device", "device_id"),
        Index("idx_video_setting_status", "status"),
    )