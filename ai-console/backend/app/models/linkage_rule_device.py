from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class LinkageRuleDevice(BaseModel):
    __tablename__ = "linkage_rule_device"

    linkage_rule_id: Mapped[int] = mapped_column(ForeignKey("linkage_rule.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False)