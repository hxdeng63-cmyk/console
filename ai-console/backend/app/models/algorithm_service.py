from sqlalchemy import String, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AlgorithmService(BaseModel):
    __tablename__ = "algorithm_service"

    service_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    service_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    service_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    service_port: Mapped[int | None] = mapped_column(nullable=True)
    annotation_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    annotation_port: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)