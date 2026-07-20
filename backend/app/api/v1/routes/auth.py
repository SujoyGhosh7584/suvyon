from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    request: UserCreate,
    auth_service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
) -> UserResponse:
    """
    Register a new user account.
    """

    user = auth_service.register(
        full_name=request.full_name,
        email=request.email,
        password=request.password,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate a user",
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    auth_service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
) -> TokenResponse:
    """
    Authenticate a user and return a JWT access token.
    """

    token = auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )

    return TokenResponse(
        access_token=token,
    )
