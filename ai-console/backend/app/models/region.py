from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Region(BaseModel):
    __tablename__ = "region"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), nullable=True)
    level: Mapped[int] = mapped_column(default=1)
    sort: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        Index("idx_region_parent", "parent_id"),
        Index("idx_region_code", "code"),
    )