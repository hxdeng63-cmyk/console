from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Organization(BaseModel):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("organization.id"), nullable=True)
    level: Mapped[int] = mapped_column(default=1)
    sort: Mapped[int] = mapped_column(default=0)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_organization_parent", "parent_id"),
        Index("idx_organization_level", "level"),
    )