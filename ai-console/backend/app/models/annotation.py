from sqlalchemy import String, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Annotation(BaseModel):
    __tablename__ = "annotation"

    deployment_id: Mapped[int | None] = mapped_column(ForeignKey("deployment.id"), nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="monitoring")
    polygon_json: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    __table_args__ = (
        Index("idx_annotation_deployment", "deployment_id"),
        Index("idx_annotation_device", "device_id"),
        Index("idx_annotation_type", "type"),
    )