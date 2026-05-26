from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeploymentDevice(BaseModel):
    __tablename__ = "deployment_device"

    deployment_id: Mapped[int] = mapped_column(ForeignKey("deployment.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)