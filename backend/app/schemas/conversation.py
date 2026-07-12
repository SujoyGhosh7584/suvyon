from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class ConversationBase(BaseSchema):
    """
    Shared conversation fields.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )


class ConversationCreate(ConversationBase):
    """
    Schema for creating a conversation.
    """

    pass


class ConversationUpdate(BaseSchema):
    """
    Schema for updating a conversation.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    is_pinned: bool | None = None

    is_archived: bool | None = None


class ConversationResponse(ConversationBase):
    """
    Schema returned by conversation endpoints.
    """

    id: UUID

    workspace_id: UUID

    is_pinned: bool

    is_archived: bool
