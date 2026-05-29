from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DataSource(BaseModel):
    __tablename__ = "data_source"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="在线", nullable=False)
    rtsp_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    push_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    access_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitude: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    org: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    memory_usage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    disk_usage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organization.id"), nullable=True)

    __table_args__ = (
        Index("idx_data_source_device", "device_id"),
        Index("idx_data_source_region", "region_id"),
        Index("idx_data_source_org", "org_id"),
    )
