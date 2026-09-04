from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.models.agent import Agent
from app.models.agent_message import AgentMessage
from app.repositories.agent_repository import AgentRepository
from app.repositories.agent_message_repository import AgentMessageRepository
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(
        self,
        repository: AgentRepository,
        message_repository: AgentMessageRepository,
    ) -> None:
        self._repo = repository
        self._messages = message_repository

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

    def get_history(self, *, agent_id: UUID) -> list[AgentMessage]:
        return self._messages.get_by_agent(agent_id)

    def get_recent_history(self, *, agent_id: UUID, limit: int = 40) -> list[AgentMessage]:
        return self._messages.get_recent_by_agent(agent_id, limit)

    def append_exchange(
        self,
        *,
        agent_id: UUID,
        user_content: str,
        assistant_content: str,
    ) -> None:
        try:
            self._messages.session.add_all(
                [
                    AgentMessage(agent_id=agent_id, role="user", content=user_content),
                    AgentMessage(agent_id=agent_id, role="assistant", content=assistant_content),
                ]
            )
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise

    def append_assistant_message(self, *, agent_id: UUID, content: str) -> None:
        try:
            self._messages.create(
                AgentMessage(agent_id=agent_id, role="assistant", content=content)
            )
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise

    def clear_history(self, *, agent_id: UUID) -> None:
        try:
            self._messages.delete_by_agent(agent_id)
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise
