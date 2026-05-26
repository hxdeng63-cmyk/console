from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PopupEventLimit(BaseModel):
    __tablename__ = "popup_event_limit"

    device_id: Mapped[int | None] = mapped_column(nullable=True)
    time_interval_seconds: Mapped[int] = mapped_column(default=0)
    response_mode: Mapped[str] = mapped_column(String(20), default="immediate")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)