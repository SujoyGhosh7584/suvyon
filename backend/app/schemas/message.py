from uuid import UUID

from pydantic import Field

from app.models.message import MessageRole
from app.schemas.base import BaseSchema


class MessageCreate(BaseSchema):
    content: str = Field(..., min_length=1, max_length=10000)
    provider: str | None = None
    model: str | None = None
    knowledge_base_id: UUID | None = None
    mode: str | None = None


class MessageResponse(BaseSchema):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    provider: str | None
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    is_edited: bool
