from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Firmware(BaseModel):
    __tablename__ = "firmware"

    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    applicable_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    force_upgrade: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)