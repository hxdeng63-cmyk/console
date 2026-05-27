from sqlalchemy import String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organization.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("idx_user_org", "org_id"),
        Index("idx_user_status", "status"),
    )