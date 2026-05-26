from datetime import datetime
from sqlalchemy import String, Index, Numeric, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CleanRecord(BaseModel):
    __tablename__ = "clean_record"

    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cutoff_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    progress: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    clean_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)

    __table_args__ = (
        Index("idx_clean_record_status", "status"),
        Index("idx_clean_record_type", "type"),
    )