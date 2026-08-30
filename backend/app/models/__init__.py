"""
Application database models.

All models must be imported here so SQLAlchemy metadata
and Alembic autogenerate can discover every table.
"""

from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.integration import Integration
from app.models.knowledge_base import KnowledgeBase
from app.models.memory import Memory
from app.models.message import Message
from app.models.otp_code import OtpCode
from app.models.tool import Tool
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.workspace import Workspace

__all__ = [
    "Agent",
    "Conversation",
    "Document",
    "Integration",
    "KnowledgeBase",
    "Memory",
    "Message",
    "OtpCode",
    "Tool",
    "User",
    "UserSettings",
    "Workspace",
]
