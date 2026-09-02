"""add conversation-scoped documents

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-02 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_bases",
        sa.Column("conversation_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_knowledge_bases_conversation_id_conversations"),
        "knowledge_bases",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_knowledge_bases_conversation_id"),
        "knowledge_bases",
        ["conversation_id"],
        unique=True,
    )

    op.add_column(
        "documents",
        sa.Column("conversation_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_documents_conversation_id_conversations"),
        "documents",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_documents_conversation_id"),
        "documents",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_conversation_id"), table_name="documents")
    op.drop_constraint(
        op.f("fk_documents_conversation_id_conversations"),
        "documents",
        type_="foreignkey",
    )
    op.drop_column("documents", "conversation_id")

    op.drop_index(
        op.f("ix_knowledge_bases_conversation_id"),
        table_name="knowledge_bases",
    )
    op.drop_constraint(
        op.f("fk_knowledge_bases_conversation_id_conversations"),
        "knowledge_bases",
        type_="foreignkey",
    )
    op.drop_column("knowledge_bases", "conversation_id")
