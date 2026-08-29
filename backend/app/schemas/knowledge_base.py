from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class KnowledgeBaseCreate(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    embedding_model: str = "text-embedding-004"


class KnowledgeBaseUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class KnowledgeBaseResponse(BaseSchema):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    embedding_model: str
    is_active: bool
