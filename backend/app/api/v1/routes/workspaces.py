from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_workspace_service
from app.api.security import get_current_verified_user
from app.models.user import User
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


@router.get(
    "",
    response_model=list[WorkspaceResponse],
    summary="List user workspaces",
)
def list_workspaces(
    current_user: Annotated[
        User,
        Depends(get_current_verified_user),
    ],
    workspace_service: Annotated[
        WorkspaceService,
        Depends(get_workspace_service),
    ],
) -> list[WorkspaceResponse]:
    """
    Retrieve all workspaces owned by the authenticated user.
    """

    workspaces = workspace_service.list_workspaces(
        owner_id=current_user.id,
    )

    return [
        WorkspaceResponse.model_validate(
            workspace,
        )
        for workspace in workspaces
    ]


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get a workspace",
)
def get_workspace(
    workspace_id: UUID,
    current_user: Annotated[
        User,
        Depends(get_current_verified_user),
    ],
    workspace_service: Annotated[
        WorkspaceService,
        Depends(get_workspace_service),
    ],
) -> WorkspaceResponse:
    """
    Retrieve a workspace owned by the authenticated user.
    """

    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    return WorkspaceResponse.model_validate(
        workspace,
    )


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workspace",
)
def create_workspace(
    request: WorkspaceCreate,
    current_user: Annotated[
        User,
        Depends(get_current_verified_user),
    ],
    workspace_service: Annotated[
        WorkspaceService,
        Depends(get_workspace_service),
    ],
) -> WorkspaceResponse:
    """
    Create a new workspace.
    """

    workspace = workspace_service.create_workspace(
        owner_id=current_user.id,
        data=request,
    )

    return WorkspaceResponse.model_validate(
        workspace,
    )


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update a workspace",
)
def update_workspace(
    workspace_id: UUID,
    request: WorkspaceUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_verified_user),
    ],
    workspace_service: Annotated[
        WorkspaceService,
        Depends(get_workspace_service),
    ],
) -> WorkspaceResponse:
    """
    Update an existing workspace.
    """

    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    workspace = workspace_service.update_workspace(
        workspace=workspace,
        data=request,
    )

    return WorkspaceResponse.model_validate(
        workspace,
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workspace",
)
def delete_workspace(
    workspace_id: UUID,
    current_user: Annotated[
        User,
        Depends(get_current_verified_user),
    ],
    workspace_service: Annotated[
        WorkspaceService,
        Depends(get_workspace_service),
    ],
) -> None:
    """
    Delete a workspace.
    """

    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    workspace_service.delete_workspace(
        workspace=workspace,
    )


@router.post(
    "/{workspace_id}/archive",
    response_model=WorkspaceResponse,
    summary="Archive a workspace",
)
def archive_workspace(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return WorkspaceResponse.model_validate(
        workspace_service.archive_workspace(workspace=workspace)
    )


@router.post(
    "/{workspace_id}/restore",
    response_model=WorkspaceResponse,
    summary="Restore an archived workspace",
)
def restore_workspace(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return WorkspaceResponse.model_validate(
        workspace_service.restore_workspace(workspace=workspace)
    )


@router.post(
    "/{workspace_id}/favourite",
    response_model=WorkspaceResponse,
    summary="Mark workspace as favourite",
)
def favourite_workspace(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return WorkspaceResponse.model_validate(
        workspace_service.set_favourite(workspace=workspace, value=True)
    )


@router.delete(
    "/{workspace_id}/favourite",
    response_model=WorkspaceResponse,
    summary="Remove workspace from favourites",
)
def unfavourite_workspace(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return WorkspaceResponse.model_validate(
        workspace_service.set_favourite(workspace=workspace, value=False)
    )
