from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, String, Text, JSON, DateTime, Index, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.core.base import Base
from app.models.base_model import BaseModel


class AgentRun(Base, BaseModel):
    __tablename__ = 'agent_runs'
    agent_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), index=True)
    workspace_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('workspaces.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(30), default='queued')
    input: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, default='')
    config: Mapped[dict] = mapped_column(JSON)
    events: Mapped[list] = mapped_column(JSON, default=list)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pending_email: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__ = (Index('uq_agent_active_run', 'agent_id', unique=True,
        postgresql_where=text("status IN ('queued', 'running', 'stopping')"),
        sqlite_where=text("status IN ('queued', 'running', 'stopping')")),)
