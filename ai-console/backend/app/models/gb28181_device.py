from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Gb28181Device(BaseModel):
    __tablename__ = "gb28181_device"

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sip_server_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sip_device_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    channels_json: Mapped[dict] = mapped_column(JSONB, default=list)

    __table_args__ = (
        Index("idx_gb28181_device_device", "device_id"),
    )