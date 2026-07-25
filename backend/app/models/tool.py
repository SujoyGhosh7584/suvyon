from enum import Enum

from sqlalchemy import Boolean, Enum as SQLEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class ToolCategory(str, Enum):
    SEARCH = "search"
    CODE = "code"
    DATA = "data"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    FILESYSTEM = "filesystem"
    INTEGRATION = "integration"
    UTILITY = "utility"


class Tool(Base, BaseModel):
    """
    Tool model.

    Represents a callable tool available to agents.
    Tools are global (not workspace-scoped).
    """

    __tablename__ = "tools"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[ToolCategory] = mapped_column(
        SQLEnum(ToolCategory, name="tool_category", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    # JSON schema string describing the tool's input parameters
    parameters_schema: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
