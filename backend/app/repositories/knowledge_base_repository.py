from uuid import UUID

from sqlalchemy import select

from app.models.knowledge_base import KnowledgeBase
from app.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    model = KnowledgeBase

    def get_by_workspace(self, workspace_id: UUID) -> list[KnowledgeBase]:
        stmt = (
            select(KnowledgeBase)
            .where(KnowledgeBase.workspace_id == workspace_id)
            .order_by(KnowledgeBase.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_id_and_workspace(
        self, kb_id: UUID, workspace_id: UUID
    ) -> KnowledgeBase | None:
        stmt = select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.workspace_id == workspace_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()
