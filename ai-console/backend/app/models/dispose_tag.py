from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DisposeTag(BaseModel):
    __tablename__ = "dispose_tag"

    tag_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tag_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    usage_count: Mapped[int] = mapped_column(default=0)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)