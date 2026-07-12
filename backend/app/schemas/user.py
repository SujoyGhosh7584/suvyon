from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """
    Shared user fields.
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class UserUpdate(BaseSchema):
    """
    Schema for updating user information.
    """

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )


class UserResponse(UserBase):
    """
    Schema returned by user endpoints.
    """

    id: UUID

    is_active: bool

    is_verified: bool

    is_superuser: bool
