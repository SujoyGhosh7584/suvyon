from uuid import UUID

from pydantic import EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdateProfile(BaseSchema):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=2048)


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
