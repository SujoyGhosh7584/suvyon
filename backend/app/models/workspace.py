from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.user import User


class Workspace(Base, BaseModel):
    """
    Workspace model.

    A workspace is the top-level container that owns
    conversations, documents, agents, and settings.
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    owner: Mapped["User"] = relationship(
        back_populates="workspaces",
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )