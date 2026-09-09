from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_github_service, get_user_service
from app.api.security import get_current_active_user
from app.models.user import User
from app.schemas.user import DeleteAccountRequest, UserResponse, UserUpdateProfile
from app.services.user_service import UserService
from app.services.github_service import GitHubService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_profile(
    request: UserUpdateProfile,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = user_service.update_profile(user=current_user, data=request)
    return UserResponse.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    request: DeleteAccountRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    github_service: Annotated[GitHubService, Depends(get_github_service)],
) -> None:
    try:
        github_service.revoke_user_installations(current_user.id)
    except Exception:
        # Account deletion must still succeed if GitHub is temporarily unavailable.
        pass
    user_service.delete_account(user=current_user)
