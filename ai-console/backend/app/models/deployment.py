from datetime import datetime, time
from sqlalchemy import String, ForeignKey, Index, DateTime, Integer
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

    # Runtime fields for local traffic algorithm subprocess management
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    log_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    module_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    deployment_token: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    org_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    region_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_deployment_algorithm", "algorithm_id"),
        Index("idx_deployment_service", "service_id"),
    )