from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class EventType(BaseModel):
    __tablename__ = "event_type"

    algorithm_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(20), default="detection")
    severity: Mapped[int] = mapped_column(default=1)
    module_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("idx_event_type_algorithm", "algorithm_id"),
        Index("idx_event_type_category", "category"),
        Index("idx_event_type_module_name", "module_name"),
    )