from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TaskDevice(BaseModel):
    __tablename__ = "task_device"

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)