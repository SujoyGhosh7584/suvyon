"""Add encrypted per-user AI provider keys."""

from alembic import op
import sqlalchemy as sa

revision = "a8b9c0d1e2f3"
down_revision = "e1f2a3b4c5d6"
branch_labels = depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_api_keys",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("encrypted_key", sa.Text(), nullable=False),
        sa.Column("key_hint", sa.String(12), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_api_keys")),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_api_keys_user_provider"),
    )
    op.create_index(op.f("ix_user_api_keys_user_id"), "user_api_keys", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_api_keys_user_id"), table_name="user_api_keys")
    op.drop_table("user_api_keys")
