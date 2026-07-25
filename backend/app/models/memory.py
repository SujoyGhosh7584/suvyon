from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class MemoryScope(str, Enum):
    PERSONAL = "personal"
    WORKSPACE = "workspace"
    CONVERSATION = "conversation"
    AGENT = "agent"


class Memory(Base, BaseModel):
    """
    Memory model.

    Stores long-term facts and context scoped to a user,
    workspace, conversation, or agent.
    """

    __tablename__ = "memories"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    scope: Mapped[MemoryScope] = mapped_column(
        SQLEnum(MemoryScope, name="memory_scope"),
        nullable=False,
        index=True,
    )

    # Optional FK to scope the memory further
    workspace_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    conversation_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    agent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
