from uuid import UUID

from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema


class AgentCreate(BaseSchema):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    instructions: str | None = Field(default=None, max_length=20_000)
    provider: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    tools: str | None = Field(default=None, max_length=4000)
    is_public: bool = False


class AgentUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    instructions: str | None = Field(default=None, max_length=20_000)
    provider: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    tools: str | None = Field(default=None, max_length=4000)
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


class AgentHistoryItem(BaseSchema):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=20_000)


class AgentMessageResponse(BaseSchema):
    role: Literal["user", "assistant"]
    content: str


class AgentRunRequest(BaseSchema):
    content: str = Field(..., min_length=1, max_length=20_000)
    history: list[AgentHistoryItem] | None = Field(default=None, max_length=40)

    @field_validator("history")
    @classmethod
    def limit_history_size(cls, value):
        if value is not None and sum(len(item.content) for item in value) > 80_000:
            raise ValueError("Agent history is too large.")
        return value


class PendingEmailDraft(BaseSchema):
    to: EmailStr
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, max_length=20_000)
    regards: str = Field(default="", max_length=500)


class AgentRunResponse(BaseSchema):
    content: str
    pending_email: PendingEmailDraft | None = None


class AgentEmailSendRequest(PendingEmailDraft):
    confirmed: Literal[True]


class AgentEmailSendResponse(BaseSchema):
    message: str
