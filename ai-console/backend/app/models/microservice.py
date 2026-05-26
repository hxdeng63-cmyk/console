from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Microservice(BaseModel):
    __tablename__ = "microservice"

    code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    port: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    cpu_usage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    memory_usage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)