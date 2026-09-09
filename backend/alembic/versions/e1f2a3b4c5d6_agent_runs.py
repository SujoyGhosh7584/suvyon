"""Persist bounded agent executions and their activity."""
from alembic import op
import sqlalchemy as sa

revision = 'e1f2a3b4c5d6'
down_revision = 'd0e1f2a3b4c5'
branch_labels = depends_on = None


def upgrade():
    op.create_table('agent_runs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('agent_id', sa.UUID(), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', sa.UUID(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('input', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('model', sa.String(200), nullable=True),
        sa.Column('pending_email', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_agent_runs_agent_id', 'agent_runs', ['agent_id'])
    op.create_index('ix_agent_runs_workspace_id', 'agent_runs', ['workspace_id'])
    op.create_index('uq_agent_active_run', 'agent_runs', ['agent_id'], unique=True,
                    postgresql_where=sa.text("status IN ('queued', 'running', 'stopping')"))


def downgrade():
    op.drop_table('agent_runs')
