from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base
from app.models.base_model import BaseModel


class OtpPurpose(str, Enum):
    VERIFY_EMAIL = "verify_email"
    RESET_PASSWORD = "reset_password"


class OtpCode(Base, BaseModel):
    """Hashed one-time codes for email verification and password reset."""

    __tablename__ = "otp_codes"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    purpose: Mapped[str] = mapped_column(String(32), nullable=False)

    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
