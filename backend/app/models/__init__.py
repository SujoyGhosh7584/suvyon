"""
Application database models.

All models must be imported here so SQLAlchemy metadata
and Alembic autogenerate can discover every table.
"""

from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.agent_message import AgentMessage
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.integration import Integration
from app.models.github_project import GitHubChangeProposal, GitHubInstallation, GitHubProject
from app.models.knowledge_base import KnowledgeBase
from app.models.memory import Memory
from app.models.message import Message
from app.models.otp_code import OtpCode
from app.models.oauth_account import OAuthAccount
from app.models.tool import Tool
from app.models.user import User
from app.models.user_api_key import UserApiKey
from app.models.user_settings import UserSettings
from app.models.workspace import Workspace

__all__ = [
    "Agent",
    "AgentRun",
    "AgentMessage",
    "Conversation",
    "Document",
    "Integration",
    "GitHubChangeProposal",
    "GitHubInstallation",
    "GitHubProject",
    "KnowledgeBase",
    "Memory",
    "Message",
    "OtpCode",
    "OAuthAccount",
    "Tool",
    "User",
    "UserApiKey",
    "UserSettings",
    "Workspace",
]
