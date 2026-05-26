from datetime import datetime, time
from sqlalchemy import String, ForeignKey, Index, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeploymentSchedule(BaseModel):
    __tablename__ = "deployment_schedule"

    deployment_id: Mapped[int] = mapped_column(ForeignKey("deployment.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    __table_args__ = (
        Index("idx_deployment_schedule_deployment", "deployment_id"),
    )