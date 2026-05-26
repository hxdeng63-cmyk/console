from sqlalchemy import String, ForeignKey, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class File(BaseModel):
    __tablename__ = "file"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_file_device", "device_id"),
        Index("idx_file_type", "file_type"),
    )