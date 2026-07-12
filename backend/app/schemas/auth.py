from pydantic import Field

from app.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """
    User login request.
    """

    email: str = Field(
        ...,
        max_length=255,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class TokenResponse(BaseSchema):
    """
    JWT authentication response.
    """

    access_token: str

    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    """
    Refresh token request.

    Reserved for future implementation.
    """

    refresh_token: str
