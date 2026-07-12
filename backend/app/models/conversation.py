from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.workspace import Workspace


class Conversation(Base, BaseModel):
    """
    Conversation model.

    A conversation belongs to a workspace and
    contains multiple chat messages.
    """

    __tablename__ = "conversations"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    workspace: Mapped["Workspace"] = relationship(
        back_populates="conversations",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
