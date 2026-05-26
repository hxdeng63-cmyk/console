from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Resource(BaseModel):
    __tablename__ = "resource"

    resource: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_group: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(20), default="GET")
    service_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("idx_resource_group", "resource_group"),
    )