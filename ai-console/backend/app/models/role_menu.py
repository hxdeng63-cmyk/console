from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RoleMenu(BaseModel):
    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), nullable=False)