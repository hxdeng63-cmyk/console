from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class EventTypePTWeight(BaseModel):
    __tablename__ = "event_type_pt_weight"

    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_type.id"), nullable=False)
    pt_weight_file_id: Mapped[int] = mapped_column(ForeignKey("pt_weight_file.id"), nullable=False)

    __table_args__ = (
        Index("idx_etpw_event_type", "event_type_id"),
        Index("idx_etpw_pt_weight", "pt_weight_file_id"),
    )
