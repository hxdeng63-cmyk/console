from sqlalchemy import String, ForeignKey, Index, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Device(BaseModel):
    __tablename__ = "device"

    device_code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    access_type: Mapped[str] = mapped_column(String(20), default="direct", nullable=False)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organization.id"), nullable=True)
    memory_usage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    disk_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    disk_usage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_device_region", "region_id"),
        Index("idx_device_org", "org_id"),
        Index("idx_device_status", "status"),
        Index("idx_device_access_type", "access_type"),
    )