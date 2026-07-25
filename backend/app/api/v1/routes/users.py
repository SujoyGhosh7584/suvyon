from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service
from app.api.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateProfile
from app.services.user_service import UserService

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
