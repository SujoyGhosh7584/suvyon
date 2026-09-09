from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_otp_service
from app.api.security import get_current_active_user, oauth2_scheme
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    EmailRequest,
    OtpSentResponse,
    OAuthExchangeRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyOtpRequest,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.otp_service import OtpService
from app.services.oauth_service import OAuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth_service = OAuthService()


@router.get("/oauth/providers")
def oauth_providers() -> dict[str, bool]:
    return {
        "google": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        "github": bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET),
    }


@router.get("/oauth/{provider}/start")
def oauth_start(provider: str) -> RedirectResponse:
    try:
        url, state = oauth_service.authorization(provider)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    response = RedirectResponse(url)
    response.set_cookie(
        "suvyon_oauth_state",
        state,
        max_age=600,
        httponly=True,
        secure=settings.APP_ENV.lower() == "production",
        samesite="lax",
    )
    return response


@router.get("/oauth/{provider}/callback")
def oauth_callback(
    provider: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    code: Annotated[str | None, Query()] = None,
    state_value: Annotated[str | None, Query(alias="state")] = None,
    error: Annotated[str | None, Query()] = None,
    cookie_state: Annotated[str | None, Cookie(alias="suvyon_oauth_state")] = None,
) -> RedirectResponse:
    try:
        if error or not code or not state_value:
            raise ValueError(error or "OAuth authorization was cancelled.")
        oauth_service.validate_state(provider, state_value, cookie_state)
        profile = oauth_service.fetch_profile(provider, code)
        user = auth_service.oauth_login(provider=provider, profile=profile)
        ticket = oauth_service.create_exchange_ticket(user.id)
        response = RedirectResponse(
            f"{settings.FRONTEND_URL.rstrip('/')}/oauth/callback?ticket={quote(ticket)}"
        )
    except Exception as exc:
        response = RedirectResponse(
            f"{settings.FRONTEND_URL.rstrip('/')}/login?oauth_error={quote(str(exc)[:300])}"
        )
    response.delete_cookie("suvyon_oauth_state")
    return response


@router.post("/oauth/exchange", response_model=TokenResponse)
def oauth_exchange(
    request: OAuthExchangeRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    try:
        user_id = oauth_service.consume_exchange_ticket(request.ticket)
        return auth_service.issue_tokens_for_user_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


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
