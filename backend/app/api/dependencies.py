from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService


def get_user_repository(
    db: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(
    db: Annotated[Session, Depends(get_db)],
) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repository=user_repository)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository=user_repository)


def get_workspace_service(
    workspace_repository: Annotated[WorkspaceRepository, Depends(get_workspace_repository)],
) -> WorkspaceService:
    return WorkspaceService(workspace_repository=workspace_repository)


def get_conversation_repository(
    db: Annotated[Session, Depends(get_db)],
) -> ConversationRepository:
    return ConversationRepository(db)


def get_message_repository(
    db: Annotated[Session, Depends(get_db)],
) -> MessageRepository:
    return MessageRepository(db)


def get_chat_service(
    conversation_repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    message_repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ChatService:
    return ChatService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )
