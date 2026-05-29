from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeviceGroup(BaseModel):
    __tablename__ = "device_group"

    group_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_count: Mapped[int] = mapped_column(default=0)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)

    __table_args__ = (
        Index("idx_device_group_region", "region_id"),
    )