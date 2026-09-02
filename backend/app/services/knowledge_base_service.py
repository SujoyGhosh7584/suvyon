from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.models.knowledge_base import KnowledgeBase
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate


class KnowledgeBaseService:
    def __init__(self, repository: KnowledgeBaseRepository) -> None:
        self._repo = repository

    def list(self, *, workspace_id: UUID) -> list[KnowledgeBase]:
        return self._repo.get_by_workspace(workspace_id)

    def get(self, *, kb_id: UUID, workspace_id: UUID) -> KnowledgeBase | None:
        return self._repo.get_by_id_and_workspace(kb_id, workspace_id)

    def get_or_create_for_conversation(
        self, *, conversation_id: UUID, workspace_id: UUID
    ) -> KnowledgeBase:
        existing = self._repo.get_by_conversation(conversation_id, workspace_id)
        if existing:
            return existing
        kb = KnowledgeBase(
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            name="Chat files",
            description="Private documents attached to one conversation.",
        )
        try:
            self._repo.create(kb)
            self._repo.commit()
            self._repo.refresh(kb)
            return kb
        except SQLAlchemyError:
            self._repo.rollback()
            raise

    def create(self, *, workspace_id: UUID, data: KnowledgeBaseCreate) -> KnowledgeBase:
        kb = KnowledgeBase(
            workspace_id=workspace_id,
            name=data.name,
            description=data.description,
            embedding_model=data.embedding_model,
        )
        try:
            self._repo.create(kb)
            self._repo.commit()
            self._repo.refresh(kb)
            return kb
        except SQLAlchemyError:
            self._repo.rollback()
            raise

    def update(self, *, kb: KnowledgeBase, data: KnowledgeBaseUpdate) -> KnowledgeBase:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(kb, field, value)
        try:
            self._repo.commit()
            return kb
        except SQLAlchemyError:
            self._repo.rollback()
            raise

    def delete(self, *, kb: KnowledgeBase) -> None:
        try:
            self._repo.delete(kb)
            self._repo.commit()
        except SQLAlchemyError:
            self._repo.rollback()
            raise
