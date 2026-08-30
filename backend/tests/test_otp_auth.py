"""OTP hashing, expiry, rate limit, and password-reset flow (no live SMTP)."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password, verify_password
from app.exceptions.auth import OtpInvalidError, OtpRateLimitedError
from app.models.otp_code import OtpPurpose
from app.services.otp_service import (
    OtpService,
    generate_otp_code,
    otp_is_expired,
    resend_wait_seconds,
)
from app.tools.email_tool import SmtpNotConfiguredError


def test_otp_is_six_digits_and_hashed():
    code = generate_otp_code()
    assert len(code) == 6
    assert code.isdigit()
    hashed = hash_password(code)
    assert hashed != code
    assert code not in hashed
    assert verify_password(code, hashed)
    assert not verify_password("000000", hashed)


def test_otp_expiry_and_resend_window():
    now = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
    assert otp_is_expired(now - timedelta(seconds=1), now)
    assert not otp_is_expired(now + timedelta(minutes=10), now)
    assert resend_wait_seconds(now, now) == 60
    assert resend_wait_seconds(now - timedelta(seconds=20), now) == 40
    assert resend_wait_seconds(now - timedelta(seconds=60), now) == 0


class _FakeOtpRepo:
    def __init__(self) -> None:
        self.rows: list = []

    def get_latest(self, email: str, purpose: str):
        matches = [row for row in self.rows if row.email == email and row.purpose == purpose]
        return matches[-1] if matches else None

    def get_latest_active(self, email: str, purpose: str):
        matches = [
            row
            for row in self.rows
            if row.email == email and row.purpose == purpose and row.consumed_at is None
        ]
        return matches[-1] if matches else None

    def consume_active(self, email: str, purpose: str, consumed_at: datetime) -> None:
        for row in self.rows:
            if row.email == email and row.purpose == purpose and row.consumed_at is None:
                row.consumed_at = consumed_at

    def create(self, entity):
        now = datetime.now(timezone.utc)
        if getattr(entity, "created_at", None) is None:
            entity.created_at = now
        if getattr(entity, "updated_at", None) is None:
            entity.updated_at = now
        self.rows.append(entity)
        return entity

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        self.rows.clear()


class _FakeUsers:
    def __init__(self, user) -> None:
        self.user = user

    def get_by_email(self, email: str):
        if self.user and self.user.email == email.lower():
            return self.user
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def refresh(self, user) -> None:
        return None


def _service(user, otp_repo=None, now=None, sent=None):
    mailbox = sent if sent is not None else []

    def fake_send(to: str, subject: str, body: str) -> None:
        mailbox.append({"to": to, "subject": subject, "body": body})

    clock = {"t": now or datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)}

    service = OtpService(
        otp_repository=otp_repo or _FakeOtpRepo(),
        user_repository=_FakeUsers(user),
        send_email=fake_send,
        require_smtp=lambda: None,
        now_fn=lambda: clock["t"],
        generate_code=lambda: "123456",
    )
    return service, mailbox, clock


def test_reset_password_flow_consumes_hashed_otp():
    user = SimpleNamespace(
        email="ada@example.com",
        is_active=True,
        hashed_password=hash_password("old-password"),
    )
    otp_repo = _FakeOtpRepo()
    service, mailbox, clock = _service(user, otp_repo=otp_repo)

    service.request_password_reset("ada@example.com")
    assert len(mailbox) == 1
    assert "123456" in mailbox[0]["body"]
    stored = otp_repo.rows[0]
    assert stored.code_hash != "123456"
    assert "123456" not in stored.code_hash
    assert verify_password("123456", stored.code_hash)

    with pytest.raises(OtpInvalidError):
        service.reset_password("ada@example.com", "000000", "new-password1")

    clock["t"] = clock["t"] + timedelta(minutes=11)
    with pytest.raises(OtpInvalidError):
        service.reset_password("ada@example.com", "123456", "new-password1")

    clock["t"] = datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc)
    stored.consumed_at = None
    stored.expires_at = clock["t"] + timedelta(minutes=10)
    service.reset_password("ada@example.com", "123456", "new-password1")
    assert verify_password("new-password1", user.hashed_password)
    assert stored.consumed_at is not None

    with pytest.raises(OtpInvalidError):
        service.reset_password("ada@example.com", "123456", "another-password")


def test_resend_is_rate_limited():
    user = SimpleNamespace(
        email="ada@example.com",
        is_active=True,
        is_verified=False,
        hashed_password="x",
    )
    service, mailbox, _clock = _service(user)
    service.send_verification("ada@example.com")
    assert len(mailbox) == 1
    with pytest.raises(OtpRateLimitedError) as exc:
        service.send_verification("ada@example.com")
    assert exc.value.retry_after_seconds > 0
    assert len(mailbox) == 1


def test_forgot_password_fails_clearly_without_smtp():
    user = SimpleNamespace(email="ada@example.com", is_active=True, hashed_password="x")
    sent: list = []

    def boom() -> None:
        raise SmtpNotConfiguredError("SMTP is not configured. Email was not sent.")

    service = OtpService(
        otp_repository=_FakeOtpRepo(),
        user_repository=_FakeUsers(user),
        send_email=lambda *args: sent.append(args),
        require_smtp=boom,
        generate_code=lambda: "123456",
    )
    with pytest.raises(SmtpNotConfiguredError, match="SMTP is not configured"):
        service.request_password_reset("ada@example.com")
    assert sent == []
