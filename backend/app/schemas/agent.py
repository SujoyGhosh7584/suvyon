from uuid import UUID

from pydantic import BaseModel

from app.schemas.base import BaseSchema


class AgentCreate(BaseSchema):
    name: str
    description: str | None = None
    instructions: str | None = None
    provider: str | None = None
    model: str | None = None
    tools: str | None = None
    is_public: bool = False


class AgentUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    provider: str | None = None
    model: str | None = None
    tools: str | None = None
    is_active: bool | None = None
    is_public: bool | None = None


class AgentResponse(BaseSchema):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    instructions: str | None
    provider: str | None
    model: str | None
    tools: str | None
    is_active: bool
    is_public: bool


class AgentRunRequest(BaseSchema):
    content: str
    history: list[dict] | None = None


class AgentRunResponse(BaseSchema):
    content: str
