from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class ChangePasswordRequest(BaseSchema):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class EmailRequest(BaseSchema):
    email: EmailStr


class VerifyOtpRequest(BaseSchema):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=12)


class ResetPasswordRequest(BaseSchema):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=12)
    new_password: str = Field(..., min_length=8, max_length=128)


class OtpSentResponse(BaseSchema):
    message: str
