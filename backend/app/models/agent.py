from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.agent_message import AgentMessage
    from app.models.workspace import Workspace


class Agent(Base, BaseModel):
    """
    Agent model.

    An agent is a configured AI persona with a specific
    purpose, instructions, tools, and provider settings.
    """

    __tablename__ = "agents"

    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)

    model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Comma-separated tool identifiers e.g. "web_search,calculator"
    tools: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    workspace: Mapped["Workspace"] = relationship(back_populates="agents")

    messages: Mapped[list["AgentMessage"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
