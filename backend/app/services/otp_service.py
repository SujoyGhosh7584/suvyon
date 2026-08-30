from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.exc import SQLAlchemyError

from app.core.constants import OTP_CODE_LENGTH, OTP_EXPIRE_MINUTES, OTP_RESEND_SECONDS
from app.core.security import hash_password, verify_password
from app.exceptions.auth import OtpInvalidError, OtpRateLimitedError
from app.models.otp_code import OtpCode, OtpPurpose
from app.models.user import User
from app.repositories.otp_repository import OtpRepository
from app.repositories.user_repository import UserRepository
from app.tools.email_tool import require_smtp as default_require_smtp
from app.tools.email_tool import send_system_email


def generate_otp_code(length: int = OTP_CODE_LENGTH) -> str:
    upper = 10 ** length
    return f"{secrets.randbelow(upper):0{length}d}"


def otp_is_expired(expires_at: datetime, now: datetime) -> bool:
    expires = expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    current = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    return current >= expires


def resend_wait_seconds(last_sent_at: datetime, now: datetime, window: int = OTP_RESEND_SECONDS) -> int:
    sent = last_sent_at
    if sent.tzinfo is None:
        sent = sent.replace(tzinfo=timezone.utc)
    current = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    elapsed = (current - sent).total_seconds()
    remaining = int(window - elapsed)
    return remaining if remaining > 0 else 0


class OtpService:
    def __init__(
        self,
        otp_repository: OtpRepository,
        user_repository: UserRepository,
        *,
        send_email: Callable[[str, str, str], None] = send_system_email,
        require_smtp: Callable[[], None] = default_require_smtp,
        now_fn: Callable[[], datetime] | None = None,
        generate_code: Callable[[], str] | None = None,
    ) -> None:
        self._otp_repository = otp_repository
        self._user_repository = user_repository
        self._send_email = send_email
        self._require_smtp = require_smtp
        self._now = now_fn or (lambda: datetime.now(timezone.utc))
        self._generate_code = generate_code or generate_otp_code

    def send_verification(self, email: str, *, commit: bool = True) -> None:
        self._require_smtp()
        normalized = _normalize_email(email)
        user = self._user_repository.get_by_email(normalized)
        if user is None or user.is_verified:
            return
        self._issue(
            email=normalized,
            purpose=OtpPurpose.VERIFY_EMAIL.value,
            subject="Your Suvyon verification code",
            intro="Use this code to verify your Suvyon email address.",
            commit=commit,
        )

    def verify_email(self, email: str, code: str) -> User:
        normalized = _normalize_email(email)
        user = self._user_repository.get_by_email(normalized)
        if user is None:
            raise OtpInvalidError()
        if user.is_verified:
            return user
        self._consume_valid_code(normalized, OtpPurpose.VERIFY_EMAIL.value, code)
        user.is_verified = True
        try:
            self._user_repository.commit()
            self._user_repository.refresh(user)
            return user
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

    def request_password_reset(self, email: str) -> None:
        self._require_smtp()
        normalized = _normalize_email(email)
        user = self._user_repository.get_by_email(normalized)
        if user is None or not user.is_active:
            return
        self._issue(
            email=normalized,
            purpose=OtpPurpose.RESET_PASSWORD.value,
            subject="Your Suvyon password reset code",
            intro="Use this code to reset your Suvyon password.",
            commit=True,
        )

    def reset_password(self, email: str, code: str, new_password: str) -> None:
        normalized = _normalize_email(email)
        user = self._user_repository.get_by_email(normalized)
        if user is None or not user.is_active:
            raise OtpInvalidError()
        self._consume_valid_code(normalized, OtpPurpose.RESET_PASSWORD.value, code)
        user.hashed_password = hash_password(new_password)
        try:
            self._user_repository.commit()
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

    def _issue(
        self,
        *,
        email: str,
        purpose: str,
        subject: str,
        intro: str,
        commit: bool,
    ) -> None:
        now = self._now()
        latest = self._otp_repository.get_latest(email, purpose)
        if latest is not None:
            wait = resend_wait_seconds(latest.created_at, now)
            if wait > 0:
                raise OtpRateLimitedError(wait)

        code = self._generate_code()
        self._otp_repository.consume_active(email, purpose, now)
        record = OtpCode(
            email=email,
            purpose=purpose,
            code_hash=hash_password(code),
            expires_at=now + timedelta(minutes=OTP_EXPIRE_MINUTES),
        )
        self._otp_repository.create(record)

        body = (
            f"{intro}\n\n"
            f"Your code is: {code}\n\n"
            f"It expires in {OTP_EXPIRE_MINUTES} minutes. "
            "If you did not request this, you can ignore this email."
        )
        try:
            self._send_email(email, subject, body)
            if commit:
                self._otp_repository.commit()
        except Exception:
            self._otp_repository.rollback()
            raise

    def _consume_valid_code(self, email: str, purpose: str, code: str) -> None:
        now = self._now()
        record = self._otp_repository.get_latest_active(email, purpose)
        if record is None or otp_is_expired(record.expires_at, now):
            raise OtpInvalidError()
        cleaned = (code or "").strip()
        if not cleaned or not verify_password(cleaned, record.code_hash):
            raise OtpInvalidError()
        record.consumed_at = now


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()
