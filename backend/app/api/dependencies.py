from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.agent_repository import AgentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.otp_repository import OtpRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agent_service import AgentService
from app.services.auth_service import AuthService
from app.services.otp_service import OtpService
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService


def get_agent_repository(
    db: Annotated[Session, Depends(get_db)],
) -> AgentRepository:
    return AgentRepository(db)


def get_agent_service(
    repository: Annotated[AgentRepository, Depends(get_agent_repository)],
) -> AgentService:
    return AgentService(repository=repository)


def get_user_repository(
    db: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(
    db: Annotated[Session, Depends(get_db)],
) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_otp_repository(
    db: Annotated[Session, Depends(get_db)],
) -> OtpRepository:
    return OtpRepository(db)


def get_otp_service(
    otp_repository: Annotated[OtpRepository, Depends(get_otp_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> OtpService:
    return OtpService(
        otp_repository=otp_repository,
        user_repository=user_repository,
    )


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    otp_service: Annotated[OtpService, Depends(get_otp_service)],
) -> AuthService:
    return AuthService(user_repository=user_repository, otp_service=otp_service)


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
    db: Annotated[Session, Depends(get_db)],
) -> ChatService:
    return ChatService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        session=db,
    )


def get_document_repository(
    db: Annotated[Session, Depends(get_db)],
) -> DocumentRepository:
    return DocumentRepository(db)


def get_knowledge_base_repository(
    db: Annotated[Session, Depends(get_db)],
) -> KnowledgeBaseRepository:
    return KnowledgeBaseRepository(db)


def get_document_service(
    document_repository: Annotated[DocumentRepository, Depends(get_document_repository)],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentService:
    return DocumentService(document_repository=document_repository, session=db)


def get_knowledge_base_service(
    repository: Annotated[KnowledgeBaseRepository, Depends(get_knowledge_base_repository)],
) -> KnowledgeBaseService:
    return KnowledgeBaseService(repository=repository)
