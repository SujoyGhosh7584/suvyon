from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class GitHubInstallation(Base, BaseModel):
    __tablename__ = "github_installations"
    __table_args__ = (
        UniqueConstraint("user_id", "installation_id", name="uq_github_user_installation"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    installation_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    account_login: Mapped[str | None] = mapped_column(String(255), nullable=True)


class GitHubProject(Base, BaseModel):
    __tablename__ = "github_projects"
    __table_args__ = (
        UniqueConstraint("workspace_id", "github_repo_id", name="uq_workspace_github_repo"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    installation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("github_installations.id", ondelete="CASCADE"),
        index=True,
    )
    github_repo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    is_private: Mapped[bool] = mapped_column(nullable=False, default=False)


class GitHubChangeProposal(Base, BaseModel):
    __tablename__ = "github_change_proposals"

    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("github_projects.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    changes: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    base_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    pull_request_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

