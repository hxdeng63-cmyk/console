from sqlalchemy import String, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AccessPlatform(BaseModel):
    __tablename__ = "access_platform"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict)