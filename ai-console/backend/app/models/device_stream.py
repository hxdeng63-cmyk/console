from sqlalchemy import String, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeviceStream(BaseModel):
    __tablename__ = "device_stream"

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)
    stream_type: Mapped[str] = mapped_column(String(20), default="main")
    stream_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    push_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[int | None] = mapped_column(nullable=True)
    codec: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")

    __table_args__ = (
        Index("idx_device_stream_device", "device_id"),
    )