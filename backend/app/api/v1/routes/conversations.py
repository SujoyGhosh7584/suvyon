from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import (
    get_chat_service,
    get_document_service,
    get_knowledge_base_service,
    get_workspace_service,
)
from app.api.security import get_current_verified_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.document import DocumentResponse
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/conversations",
    tags=["Conversations"],
)


def _get_workspace_or_404(
    workspace_id: UUID,
    current_user: User,
    workspace_service: WorkspaceService,
):
    workspace = workspace_service.get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found."
        )
    return workspace


def _get_conversation_or_404(
    workspace_id: UUID,
    conversation_id: UUID,
    current_user: User,
    workspace_service: WorkspaceService,
    chat_service: ChatService,
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    conversation = chat_service.get_conversation(
        conversation_id=conversation_id,
        workspace_id=workspace_id,
    )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
        )
    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[ConversationResponse]:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return [
        ConversationResponse.model_validate(c)
        for c in chat_service.list_conversations(workspace_id=workspace_id)
    ]


@router.post(
    "", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
def create_conversation(
    workspace_id: UUID,
    request: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ConversationResponse:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    conversation = chat_service.create_conversation(
        workspace_id=workspace_id, data=request
    )
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    workspace_id: UUID,
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ConversationResponse:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    return ConversationResponse.model_validate(conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    workspace_id: UUID,
    conversation_id: UUID,
    request: ConversationUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ConversationResponse:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    return ConversationResponse.model_validate(
        chat_service.update_conversation(conversation=conversation, data=request)
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    workspace_id: UUID,
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> None:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    chat_service.delete_conversation(conversation=conversation)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(
    workspace_id: UUID,
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[MessageResponse]:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    return [
        MessageResponse.model_validate(m)
        for m in chat_service.get_messages(conversation_id=conversation.id)
    ]


@router.get("/{conversation_id}/documents", response_model=list[DocumentResponse])
def get_conversation_documents(
    workspace_id: UUID,
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    return [
        DocumentResponse.model_validate(document)
        for document in document_service.list_conversation_documents(
            conversation_id=conversation.id,
            workspace_id=workspace_id,
        )
    ]


@router.post(
    "/{conversation_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_conversation_document(
    workspace_id: UUID,
    conversation_id: UUID,
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    kb_service: Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)],
) -> DocumentResponse:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    knowledge_base = kb_service.get_or_create_for_conversation(
        conversation_id=conversation.id,
        workspace_id=workspace_id,
    )
    try:
        document = document_service.upload(
            workspace_id=workspace_id,
            conversation_id=conversation.id,
            knowledge_base_id=knowledge_base.id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return DocumentResponse.model_validate(document)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    workspace_id: UUID,
    conversation_id: UUID,
    request: MessageCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> MessageResponse:
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    # Always apply the UI selection for this request. Empty Auto/Default
    # clears a leftover Groq id so Gemini/OpenRouter can actually run.
    conversation.provider = (request.provider or "").strip() or None
    conversation.model = (request.model or "").strip() or None

    try:
        assistant_msg = chat_service.send_message(
            conversation=conversation,
            content=request.content,
            knowledge_base_id=request.knowledge_base_id,
            knowledge_base_ids=request.knowledge_base_ids,
            mode=request.mode,
        )
        return MessageResponse.model_validate(assistant_msg)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc) or "Failed to generate AI response.",
        )


@router.post("/{conversation_id}/messages/stream")
def stream_message(
    workspace_id: UUID,
    conversation_id: UUID,
    request: MessageCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> StreamingResponse:
    """
    Stream the assistant reply as Server-Sent Events.
    Each event is a raw text chunk. The client reassembles them.
    """
    conversation = _get_conversation_or_404(
        workspace_id, conversation_id, current_user, workspace_service, chat_service
    )
    conversation.provider = (request.provider or "").strip() or None
    conversation.model = (request.model or "").strip() or None

    def event_stream():
        try:
            for chunk in chat_service.stream_message(
                conversation=conversation,
                content=request.content,
                mode=request.mode,
                knowledge_base_id=request.knowledge_base_id,
                knowledge_base_ids=request.knowledge_base_ids,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            yield f"data: Error: {str(exc)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
