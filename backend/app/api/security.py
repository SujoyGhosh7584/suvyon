from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.api.dependencies import get_user_repository
from app.core.security import get_jti, get_subject_from_token
from app.core.token_blacklist import is_blacklisted
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jti = get_jti(token)
        if is_blacklisted(jti):
            raise credentials_exception

        user_id = get_subject_from_token(token, expected_type="access")

    except JWTError:
        raise credentials_exception

    user = user_repository.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )
    return current_user


def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before using the workspace.",
        )
    return current_user
