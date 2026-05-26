from datetime import datetime
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class License(BaseModel):
    __tablename__ = "license"

    license_key: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_limit: Mapped[int] = mapped_column(default=0)
    used_count: Mapped[int] = mapped_column(default=0)
    expire_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)