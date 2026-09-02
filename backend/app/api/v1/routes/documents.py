from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import get_document_service, get_knowledge_base_service, get_workspace_service
from app.api.security import get_current_verified_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/documents",
    tags=["Documents"],
)


def _get_workspace_or_404(workspace_id, current_user, workspace_service):
    ws = workspace_service.get_workspace(workspace_id=workspace_id, owner_id=current_user.id)
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return ws


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return [
        DocumentResponse.model_validate(d)
        for d in document_service.list_documents(workspace_id=workspace_id)
    ]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    workspace_id: UUID,
    knowledge_base_id: Annotated[UUID, Form()],
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> DocumentResponse:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    knowledge_base = kb_service.get(kb_id=knowledge_base_id, workspace_id=workspace_id)
    if (
        knowledge_base is None
        or not knowledge_base.is_active
        or knowledge_base.conversation_id is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active knowledge base not found.",
        )

    try:
        document = document_service.upload(
            workspace_id=workspace_id,
            knowledge_base_id=knowledge_base_id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    workspace_id: UUID,
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> None:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    document = document_service.get_document(document_id=document_id, workspace_id=workspace_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    document_service.delete_document(document=document)
