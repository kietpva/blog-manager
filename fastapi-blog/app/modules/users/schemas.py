from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    auth_id: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserRead(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
