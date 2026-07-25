from uuid import UUID

from sqlalchemy import select

from app.models.conversation import Conversation
from app.repositories.base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    def get_by_workspace(self, workspace_id: UUID) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.workspace_id == workspace_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_id_and_workspace(
        self, conversation_id: UUID, workspace_id: UUID
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.workspace_id == workspace_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()
