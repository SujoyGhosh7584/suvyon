from uuid import UUID

from sqlalchemy import select

from app.models.agent import Agent
from app.repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    model = Agent

    def get_by_workspace(self, workspace_id: UUID) -> list[Agent]:
        stmt = (
            select(Agent)
            .where(Agent.workspace_id == workspace_id)
            .order_by(Agent.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_id_and_workspace(self, agent_id: UUID, workspace_id: UUID) -> Agent | None:
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.workspace_id == workspace_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()
