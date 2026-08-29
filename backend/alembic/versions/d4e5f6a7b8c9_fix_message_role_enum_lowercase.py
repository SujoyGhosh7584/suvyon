"""fix message_role enum to lowercase

Revision ID: d4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-07-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE message_role RENAME VALUE 'USER' TO 'user'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'ASSISTANT' TO 'assistant'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'SYSTEM' TO 'system'")


def downgrade() -> None:
    op.execute("ALTER TYPE message_role RENAME VALUE 'user' TO 'USER'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'assistant' TO 'ASSISTANT'")
    op.execute("ALTER TYPE message_role RENAME VALUE 'system' TO 'SYSTEM'")
