from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RoleResource(BaseModel):
    __tablename__ = "role_resource"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)