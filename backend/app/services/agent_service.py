from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.models.agent import Agent
from app.repositories.agent_repository import AgentRepository
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, repository: AgentRepository) -> None:
        self._repo = repository

    def list_agents(self, *, workspace_id: UUID) -> list[Agent]:
        return self._repo.get_by_workspace(workspace_id)

    def get_agent(self, *, agent_id: UUID, workspace_id: UUID) -> Agent | None:
        return self._repo.get_by_id_and_workspace(agent_id, workspace_id)

    def create_agent(self, *, workspace_id: UUID, data: AgentCreate) -> Agent:
        agent = Agent(workspace_id=workspace_id, **data.model_dump())
        try:
            self._repo.create(agent)
            self._repo.commit()
            self._repo.refresh(agent)
            return agent
        except SQLAlchemyError:
            self._repo.rollback()
            raise

    def update_agent(self, *, agent: Agent, data: AgentUpdate) -> Agent:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(agent, field, value)
        try:
            self._repo.commit()
            return agent
        except SQLAlchemyError:
            self._repo.rollback()
            raise

    def delete_agent(self, *, agent: Agent) -> None:
        try:
            self._repo.delete(agent)
            self._repo.commit()
        except SQLAlchemyError:
            self._repo.rollback()
            raise
