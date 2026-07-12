from uuid import UUID

from pydantic import Field

from app.models.message import MessageRole
from app.schemas.base import BaseSchema


class MessageBase(BaseSchema):
    """
    Shared message fields.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class MessageCreate(MessageBase):
    """
    Schema for creating a new user message.
    """

    pass


class MessageResponse(MessageBase):
    """
    Schema returned by message endpoints.
    """

    id: UUID

    conversation_id: UUID

    role: MessageRole
