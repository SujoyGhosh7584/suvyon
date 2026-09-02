from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_knowledge_base_service, get_workspace_service
from app.api.security import get_current_verified_user
from app.models.user import User
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
)
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/knowledge-bases",
    tags=["Knowledge Bases"],
)


def _get_workspace_or_404(workspace_id, current_user, workspace_service):
    ws = workspace_service.get_workspace(workspace_id=workspace_id, owner_id=current_user.id)
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return ws


def _get_kb_or_404(workspace_id, kb_id, current_user, workspace_service, kb_service):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    kb = kb_service.get(kb_id=kb_id, workspace_id=workspace_id)
    if kb is None or kb.conversation_id is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found.")
    return kb


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_knowledge_bases(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> list[KnowledgeBaseResponse]:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return [KnowledgeBaseResponse.model_validate(kb) for kb in kb_service.list(workspace_id=workspace_id)]


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_base(
    workspace_id: UUID,
    request: KnowledgeBaseCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> KnowledgeBaseResponse:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return KnowledgeBaseResponse.model_validate(
        kb_service.create(workspace_id=workspace_id, data=request)
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(
    workspace_id: UUID,
    kb_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> KnowledgeBaseResponse:
    kb = _get_kb_or_404(workspace_id, kb_id, current_user, workspace_service, kb_service)
    return KnowledgeBaseResponse.model_validate(kb)


@router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(
    workspace_id: UUID,
    kb_id: UUID,
    request: KnowledgeBaseUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> KnowledgeBaseResponse:
    kb = _get_kb_or_404(workspace_id, kb_id, current_user, workspace_service, kb_service)
    return KnowledgeBaseResponse.model_validate(kb_service.update(kb=kb, data=request))


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base(
    workspace_id: UUID,
    kb_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> None:
    kb = _get_kb_or_404(workspace_id, kb_id, current_user, workspace_service, kb_service)
    kb_service.delete(kb=kb)
