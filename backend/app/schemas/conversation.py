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
    parent_conversation_id: UUID | None = None


class ConversationBranch(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    through_message_id: UUID | None = None


class ConversationMerge(BaseSchema):
    conversation_ids: list[UUID] = Field(min_length=2, max_length=4)
    title: str = Field(default="Merged perspectives", min_length=1, max_length=255)
    focus: str = Field(default="Find the strongest approach and a concrete next step.", min_length=1, max_length=2000)
    provider: str | None = None
    model: str | None = None
