from __future__ import annotations

import enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, BaseModel
from sqlalchemy import Enum, Boolean


class UserRole(enum.Enum):
    admin = "admin"
    user = "user"


class User(Base, BaseModel):
    __tablename__ = "users"

    auth_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False),
        nullable=False,
        default=UserRole.user,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
