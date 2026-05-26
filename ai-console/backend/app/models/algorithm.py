from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Algorithm(BaseModel):
    __tablename__ = "algorithm"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    business_category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("idx_algorithm_category", "business_category"),
    )