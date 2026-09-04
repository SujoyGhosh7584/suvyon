from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentMessage(Base, BaseModel):
    """A durable user or assistant message belonging to one agent."""

    __tablename__ = "agent_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="valid_role"),
    )

    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    agent: Mapped["Agent"] = relationship(back_populates="messages")
