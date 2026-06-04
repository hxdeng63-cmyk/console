from datetime import datetime, time
from sqlalchemy import String, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Deployment(BaseModel):
    __tablename__ = "deployment"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm.id"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("algorithm_service.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    algorithm_status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    schedule: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_deployment_algorithm", "algorithm_id"),
        Index("idx_deployment_service", "service_id"),
    )