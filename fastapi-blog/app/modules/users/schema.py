from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.users.model import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    auth_id: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class AdminUserUpdate(UserUpdate):
    role: UserRole | None = None
    is_active: bool | None = None


class UserBaseRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str


class UserRead(UserBaseRead):
    pass


class AdminUserRead(UserBaseRead):
    auth_id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
