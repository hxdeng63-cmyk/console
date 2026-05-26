from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class WarningEventTag(BaseModel):
    __tablename__ = "warning_event_tag"

    warning_event_id: Mapped[int] = mapped_column(ForeignKey("warning_event.id"), nullable=False)
    dispose_tag_id: Mapped[int] = mapped_column(ForeignKey("dispose_tag.id"), nullable=False)