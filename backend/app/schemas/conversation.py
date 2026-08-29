from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class ConversationCreate(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    provider: str | None = None
    model: str | None = None
    system_prompt: str | None = None


class ConversationUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    provider: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    is_pinned: bool | None = None
    is_archived: bool | None = None


class ConversationResponse(BaseSchema):
    id: UUID
    workspace_id: UUID
    title: str
    provider: str | None
    model: str | None
    system_prompt: str | None
    is_pinned: bool
    is_archived: bool
