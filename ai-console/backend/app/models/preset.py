from sqlalchemy import String, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Preset(BaseModel):
    __tablename__ = "preset"

    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    p: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    t: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    z: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    time_range_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_preset_device", "device_id"),
    )