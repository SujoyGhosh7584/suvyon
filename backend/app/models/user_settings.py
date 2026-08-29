from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class UserSettings(Base, BaseModel):
    """
    User settings model.

    Stores per-user preferences and AI configuration defaults.
    One row per user (1-to-1 with User).
    """

    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # UI preferences
    theme: Mapped[str] = mapped_column(String(50), default="dark", nullable=False)

    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # AI defaults
    default_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)

    default_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Notifications
    email_notifications: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
