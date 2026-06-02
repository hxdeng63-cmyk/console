from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class CleanupPolicy(BaseModel):
    __tablename__ = "cleanup_policy"

    alert_enabled: Mapped[bool] = mapped_column(default=True)
    alert_days: Mapped[int] = mapped_column(default=90)
    video_enabled: Mapped[bool] = mapped_column(default=True)
    video_days: Mapped[int] = mapped_column(default=60)
    strategy: Mapped[str] = mapped_column(String(20), default="scheduled")
    execute_time: Mapped[str | None] = mapped_column(String(5), default="02:00")
