from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeviceGroupMembership(BaseModel):
    __tablename__ = "device_group_membership"

    device_group_id: Mapped[int] = mapped_column(ForeignKey("device_group.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)