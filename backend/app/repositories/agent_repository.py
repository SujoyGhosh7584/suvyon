from uuid import UUID

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_workspace(self, workspace_id: UUID) -> list[Agent]:
        return self._session.query(Agent).filter(Agent.workspace_id == workspace_id).all()

    def get_by_id_and_workspace(self, agent_id: UUID, workspace_id: UUID) -> Agent | None:
        return (
            self._session.query(Agent)
            .filter(Agent.id == agent_id, Agent.workspace_id == workspace_id)
            .first()
        )
