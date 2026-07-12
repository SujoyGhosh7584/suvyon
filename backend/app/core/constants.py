"""
Application-wide constants.

Do not hardcode values throughout the codebase.
Import constants from this module instead.
"""

# ==========================================================
# User Roles
# ==========================================================

ROLE_USER = "user"
ROLE_ADMIN = "admin"


# ==========================================================
# Token Types
# ==========================================================

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


# ==========================================================
# Pagination
# ==========================================================

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# ==========================================================
# File Upload
# ==========================================================

MAX_FILE_SIZE_MB = 25

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


# ==========================================================
# Conversation
# ==========================================================

DEFAULT_CHAT_TITLE = "New Conversation"

MAX_CONVERSATION_TITLE_LENGTH = 100


# ==========================================================
# AI
# ==========================================================

DEFAULT_LLM_PROVIDER = "auto"

MAX_PROMPT_LENGTH = 50000


# ==========================================================
# API
# ==========================================================

API_HEALTH_STATUS = "healthy"


# ==========================================================
# Application
# ==========================================================

UTC = "UTC"
