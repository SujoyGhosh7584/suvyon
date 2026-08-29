from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class IntegrationProvider(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    DROPBOX = "dropbox"
    SLACK = "slack"
    DISCORD = "discord"
    NOTION = "notion"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    MICROSOFT_365 = "microsoft_365"


class Integration(Base, BaseModel):
    """
    Integration model.

    Stores a user's connected third-party service credentials
    scoped optionally to a workspace.
    """

    __tablename__ = "integrations"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    provider: Mapped[IntegrationProvider] = mapped_column(
        SQLEnum(IntegrationProvider, name="integration_provider", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    # Encrypted token stored as opaque string
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    account_label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
