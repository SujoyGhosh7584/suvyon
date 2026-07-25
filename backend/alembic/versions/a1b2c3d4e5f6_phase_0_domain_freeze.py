"""phase 0 domain freeze

Revision ID: a1b2c3d4e5f6
Revises: 5bde10682002
Create Date: 2026-07-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "5bde10682002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users — add role, avatar_url
    # ------------------------------------------------------------------
    op.add_column("users", sa.Column("role", sa.String(50), nullable=False, server_default="user"))
    op.add_column("users", sa.Column("avatar_url", sa.String(2048), nullable=True))

    # ------------------------------------------------------------------
    # workspaces — add is_archived, is_favourite
    # ------------------------------------------------------------------
    op.add_column("workspaces", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("workspaces", sa.Column("is_favourite", sa.Boolean(), nullable=False, server_default="false"))

    # ------------------------------------------------------------------
    # conversations — add provider, model, system_prompt
    # ------------------------------------------------------------------
    op.add_column("conversations", sa.Column("provider", sa.String(100), nullable=True))
    op.add_column("conversations", sa.Column("model", sa.String(100), nullable=True))
    op.add_column("conversations", sa.Column("system_prompt", sa.Text(), nullable=True))

    # ------------------------------------------------------------------
    # messages — add provider, model, token usage, is_edited
    # ------------------------------------------------------------------
    op.add_column("messages", sa.Column("provider", sa.String(100), nullable=True))
    op.add_column("messages", sa.Column("model", sa.String(100), nullable=True))
    op.add_column("messages", sa.Column("prompt_tokens", sa.Integer(), nullable=True))
    op.add_column("messages", sa.Column("completion_tokens", sa.Integer(), nullable=True))
    op.add_column("messages", sa.Column("is_edited", sa.Boolean(), nullable=False, server_default="false"))

    # ------------------------------------------------------------------
    # tools
    # ------------------------------------------------------------------
    op.create_table(
        "tools",
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "search", "code", "data", "communication",
                "productivity", "filesystem", "integration", "utility",
                name="tool_category",
            ),
            nullable=False,
        ),
        sa.Column("parameters_schema", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("requires_auth", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tools")),
        sa.UniqueConstraint("name", name=op.f("uq_tools_name")),
    )

    # ------------------------------------------------------------------
    # documents
    # ------------------------------------------------------------------
    op.create_table(
        "documents",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(2048), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "ready", "failed", name="document_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"],
            name=op.f("fk_documents_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
    )
    op.create_index(op.f("ix_documents_workspace_id"), "documents", ["workspace_id"], unique=False)

    # ------------------------------------------------------------------
    # knowledge_bases
    # ------------------------------------------------------------------
    op.create_table(
        "knowledge_bases",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=False, server_default="text-embedding-3-small"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"],
            name=op.f("fk_knowledge_bases_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_bases")),
    )
    op.create_index(op.f("ix_knowledge_bases_workspace_id"), "knowledge_bases", ["workspace_id"], unique=False)

    # ------------------------------------------------------------------
    # agents
    # ------------------------------------------------------------------
    op.create_table(
        "agents",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("tools", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"],
            name=op.f("fk_agents_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agents")),
    )
    op.create_index(op.f("ix_agents_workspace_id"), "agents", ["workspace_id"], unique=False)

    # ------------------------------------------------------------------
    # memories
    # ------------------------------------------------------------------
    op.create_table(
        "memories",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "scope",
            sa.Enum("personal", "workspace", "conversation", "agent", name="memory_scope"),
            nullable=False,
        ),
        sa.Column("workspace_id", sa.UUID(), nullable=True),
        sa.Column("conversation_id", sa.UUID(), nullable=True),
        sa.Column("agent_id", sa.UUID(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_memories_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], name=op.f("fk_memories_workspace_id_workspaces"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name=op.f("fk_memories_conversation_id_conversations"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], name=op.f("fk_memories_agent_id_agents"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_memories")),
    )
    op.create_index(op.f("ix_memories_user_id"), "memories", ["user_id"], unique=False)
    op.create_index(op.f("ix_memories_scope"), "memories", ["scope"], unique=False)
    op.create_index(op.f("ix_memories_workspace_id"), "memories", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_memories_conversation_id"), "memories", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_memories_agent_id"), "memories", ["agent_id"], unique=False)

    # ------------------------------------------------------------------
    # integrations
    # ------------------------------------------------------------------
    op.create_table(
        "integrations",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=True),
        sa.Column(
            "provider",
            sa.Enum(
                "github", "gitlab", "google_drive", "onedrive", "dropbox",
                "slack", "discord", "notion", "jira", "confluence", "microsoft_365",
                name="integration_provider",
            ),
            nullable=False,
        ),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("account_label", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_integrations_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], name=op.f("fk_integrations_workspace_id_workspaces"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integrations")),
    )
    op.create_index(op.f("ix_integrations_user_id"), "integrations", ["user_id"], unique=False)
    op.create_index(op.f("ix_integrations_workspace_id"), "integrations", ["workspace_id"], unique=False)

    # ------------------------------------------------------------------
    # user_settings
    # ------------------------------------------------------------------
    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("theme", sa.String(50), nullable=False, server_default="dark"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("default_provider", sa.String(100), nullable=True),
        sa.Column("default_model", sa.String(100), nullable=True),
        sa.Column("email_notifications", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_settings_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_settings")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_settings_user_id")),
    )
    op.create_index(op.f("ix_user_settings_user_id"), "user_settings", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_table("user_settings")

    op.drop_index(op.f("ix_integrations_workspace_id"), table_name="integrations")
    op.drop_index(op.f("ix_integrations_user_id"), table_name="integrations")
    op.drop_table("integrations")
    op.execute("DROP TYPE IF EXISTS integration_provider")

    op.drop_index(op.f("ix_memories_agent_id"), table_name="memories")
    op.drop_index(op.f("ix_memories_conversation_id"), table_name="memories")
    op.drop_index(op.f("ix_memories_workspace_id"), table_name="memories")
    op.drop_index(op.f("ix_memories_scope"), table_name="memories")
    op.drop_index(op.f("ix_memories_user_id"), table_name="memories")
    op.drop_table("memories")
    op.execute("DROP TYPE IF EXISTS memory_scope")

    op.drop_index(op.f("ix_agents_workspace_id"), table_name="agents")
    op.drop_table("agents")

    op.drop_index(op.f("ix_knowledge_bases_workspace_id"), table_name="knowledge_bases")
    op.drop_table("knowledge_bases")

    op.drop_index(op.f("ix_documents_workspace_id"), table_name="documents")
    op.drop_table("documents")
    op.execute("DROP TYPE IF EXISTS document_status")

    op.drop_table("tools")
    op.execute("DROP TYPE IF EXISTS tool_category")

    op.drop_column("messages", "is_edited")
    op.drop_column("messages", "completion_tokens")
    op.drop_column("messages", "prompt_tokens")
    op.drop_column("messages", "model")
    op.drop_column("messages", "provider")

    op.drop_column("conversations", "system_prompt")
    op.drop_column("conversations", "model")
    op.drop_column("conversations", "provider")

    op.drop_column("workspaces", "is_favourite")
    op.drop_column("workspaces", "is_archived")

    op.drop_column("users", "avatar_url")
    op.drop_column("users", "role")
