from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, ForeignKey, Index, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class FileSourceType(str, PyEnum):
    WARNING_EVENT_IMAGE = "warning_event_image"
    WARNING_EVENT_VIDEO = "warning_event_video"


class File(BaseModel):
    __tablename__ = "file"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    warning_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("warning_event.id"), nullable=True
    )
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Relationships
    warning_event: Mapped[Optional["WarningEvent"]] = relationship(
        "WarningEvent", back_populates="files"
    )

    __table_args__ = (
        Index("idx_file_device", "device_id"),
        Index("idx_file_type", "file_type"),
        Index("idx_file_warning_event", "warning_event_id"),
        Index("idx_file_source_type", "source_type"),
        Index("idx_file_warning_source", "warning_event_id", "source_type"),
        Index("idx_file_warning_event_source_unique", "warning_event_id", "source_type",
              unique=True, postgresql_where=(text("deleted_at IS NULL"))),
        Index("idx_file_source_created", "source_type", "created_at",
              postgresql_where=(text("deleted_at IS NULL"))),
    )