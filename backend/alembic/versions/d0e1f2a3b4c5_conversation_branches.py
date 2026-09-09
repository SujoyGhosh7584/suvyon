"""Track the source of a conversation branch."""
from alembic import op
import sqlalchemy as sa

revision = "d0e1f2a3b4c5"
down_revision = "c9d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("conversations", sa.Column("parent_conversation_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_conversation_parent", "conversations", "conversations",
                          ["parent_conversation_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_conversations_parent_conversation_id", "conversations", ["parent_conversation_id"])


def downgrade():
    op.drop_index("ix_conversations_parent_conversation_id", table_name="conversations")
    op.drop_constraint("fk_conversation_parent", "conversations", type_="foreignkey")
    op.drop_column("conversations", "parent_conversation_id")
