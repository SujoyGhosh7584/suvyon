from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class MessageRole(str, Enum):
    """
    Supported message roles.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base, BaseModel):
    """
    Chat message model.

    Stores both user messages and AI responses.
    """

    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(
            MessageRole,
            name="message_role",
        ),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )
