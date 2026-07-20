from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService


def get_user_repository(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> UserRepository:
    """
    Provide a UserRepository instance.
    """

    return UserRepository(
        db,
    )


def get_workspace_repository(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> WorkspaceRepository:
    """
    Provide a WorkspaceRepository instance.
    """

    return WorkspaceRepository(
        db,
    )


def get_auth_service(
    user_repository: Annotated[
        UserRepository,
        Depends(get_user_repository),
    ],
) -> AuthService:
    """
    Provide an AuthService instance.
    """

    return AuthService(
        user_repository=user_repository,
    )


def get_workspace_service(
    workspace_repository: Annotated[
        WorkspaceRepository,
        Depends(get_workspace_repository),
    ],
) -> WorkspaceService:
    """
    Provide a WorkspaceService instance.
    """

    return WorkspaceService(
        workspace_repository=workspace_repository,
    )
