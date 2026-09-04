from uuid import UUID

from sqlalchemy import delete, select

from app.models.agent_message import AgentMessage
from app.repositories.base_repository import BaseRepository


class AgentMessageRepository(BaseRepository[AgentMessage]):
    model = AgentMessage

    def get_by_agent(self, agent_id: UUID) -> list[AgentMessage]:
        stmt = (
            select(AgentMessage)
            .where(AgentMessage.agent_id == agent_id)
            .order_by(AgentMessage.created_at.asc(), AgentMessage.id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_recent_by_agent(self, agent_id: UUID, limit: int) -> list[AgentMessage]:
        stmt = (
            select(AgentMessage)
            .where(AgentMessage.agent_id == agent_id)
            .order_by(AgentMessage.created_at.desc(), AgentMessage.id.desc())
            .limit(limit)
        )
        return list(reversed(self.session.execute(stmt).scalars().all()))

    def delete_by_agent(self, agent_id: UUID) -> None:
        self.session.execute(delete(AgentMessage).where(AgentMessage.agent_id == agent_id))
