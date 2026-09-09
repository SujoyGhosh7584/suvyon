"""add oauth identities and github projects

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-09-04 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _base_columns():
    return (
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def upgrade() -> None:
    op.create_table(
        "oauth_accounts",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        *_base_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        sa.UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )
    op.create_index(op.f("ix_oauth_accounts_user_id"), "oauth_accounts", ["user_id"])

    op.create_table(
        "github_installations",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("installation_id", sa.BigInteger(), nullable=False),
        sa.Column("account_login", sa.String(255), nullable=True),
        *_base_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "installation_id", name="uq_github_user_installation"),
    )
    op.create_index(op.f("ix_github_installations_user_id"), "github_installations", ["user_id"])
    op.create_index(op.f("ix_github_installations_installation_id"), "github_installations", ["installation_id"])

    op.create_table(
        "github_projects",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("installation_id", sa.UUID(), nullable=False),
        sa.Column("github_repo_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(500), nullable=False),
        sa.Column("default_branch", sa.String(255), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        *_base_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["installation_id"], ["github_installations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "github_repo_id", name="uq_workspace_github_repo"),
    )
    op.create_index(op.f("ix_github_projects_user_id"), "github_projects", ["user_id"])
    op.create_index(op.f("ix_github_projects_workspace_id"), "github_projects", ["workspace_id"])
    op.create_index(op.f("ix_github_projects_installation_id"), "github_projects", ["installation_id"])

    op.create_table(
        "github_change_proposals",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("base_sha", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("pull_request_url", sa.String(2048), nullable=True),
        *_base_columns(),
        sa.ForeignKeyConstraint(["project_id"], ["github_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_github_change_proposals_project_id"), "github_change_proposals", ["project_id"])
    op.create_index(op.f("ix_github_change_proposals_user_id"), "github_change_proposals", ["user_id"])


def downgrade() -> None:
    op.drop_table("github_change_proposals")
    op.drop_table("github_projects")
    op.drop_table("github_installations")
    op.drop_table("oauth_accounts")
