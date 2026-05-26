from sqlalchemy import String, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Menu(BaseModel):
    __tablename__ = "menu"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    path: Mapped[str | None] = mapped_column(String(200), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menu.id"), nullable=True)
    sort: Mapped[int] = mapped_column(default=0)
    component: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_menu_parent", "parent_id"),
        Index("idx_menu_sort", "sort"),
    )