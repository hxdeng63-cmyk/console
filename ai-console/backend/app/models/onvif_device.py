from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OnvifDevice(BaseModel):
    __tablename__ = "onvif_device"

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    port: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    profiles_json: Mapped[dict] = mapped_column(JSONB, default=list)

    __table_args__ = (
        Index("idx_onvif_device_device", "device_id"),
    )