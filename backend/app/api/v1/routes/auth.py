from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_otp_service
from app.api.security import get_current_active_user, oauth2_scheme
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    EmailRequest,
    OtpSentResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyOtpRequest,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OtpService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = auth_service.register(
        full_name=request.full_name,
        email=request.email,
        password=request.password,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return auth_service.refresh(refresh_token=request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    auth_service.logout(access_token=token)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    auth_service.change_password(
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
    )


@router.post("/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate(
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    auth_service.deactivate(user=current_user)


@router.post("/verify-email", response_model=UserResponse)
def verify_email(
    request: VerifyOtpRequest,
    otp_service: Annotated[OtpService, Depends(get_otp_service)],
) -> UserResponse:
    user = otp_service.verify_email(request.email, request.code)
    return UserResponse.model_validate(user)


@router.post("/resend-verification", response_model=OtpSentResponse)
def resend_verification(
    request: EmailRequest,
    otp_service: Annotated[OtpService, Depends(get_otp_service)],
) -> OtpSentResponse:
    otp_service.send_verification(request.email)
    return OtpSentResponse(message="If this email needs verification, we sent a code.")


@router.post("/forgot-password", response_model=OtpSentResponse)
def forgot_password(
    request: EmailRequest,
    otp_service: Annotated[OtpService, Depends(get_otp_service)],
) -> OtpSentResponse:
    otp_service.request_password_reset(request.email)
    return OtpSentResponse(message="If that account exists, we sent a reset code.")


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    request: ResetPasswordRequest,
    otp_service: Annotated[OtpService, Depends(get_otp_service)],
) -> None:
    otp_service.reset_password(
        email=request.email,
        code=request.code,
        new_password=request.new_password,
    )
