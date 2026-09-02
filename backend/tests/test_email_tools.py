"""Email tools draft without sending, and send only after confirmation."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools import email_tool as email_tools


def test_user_confirmed_send_rejects_compose_requests():
    assert not email_tools.user_confirmed_send("Send an email to ada@example.com about the meeting")
    assert not email_tools.user_confirmed_send("Draft a note to bob@example.com")
    assert email_tools.user_confirmed_send("send it")
    assert email_tools.user_confirmed_send("yes")


def test_draft_email_does_not_send():
    result = email_tools.draft_email(
        "ada@example.com",
        "Meeting",
        "Can we move tomorrow's call to 3pm?",
    )
    assert "To: ada@example.com" in result
    assert "has not been sent" in result


def test_send_email_blocked_without_confirmation(monkeypatch):
    sent = {"n": 0}

    def fake_smtp(*args, **kwargs):
        sent["n"] += 1
        raise AssertionError("SMTP should not be used before confirmation")

    monkeypatch.setattr(email_tools.smtplib, "SMTP", fake_smtp)
    result = email_tools.send_email(
        "ada@example.com",
        "Meeting",
        "See you at 3.",
        user_content="Send an email to ada@example.com about the meeting",
    )
    assert result.startswith("BLOCKED")
    assert sent["n"] == 0


def test_send_email_sends_after_confirmation(monkeypatch):
    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            self.sent = None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def ehlo(self):
            return None

        def starttls(self):
            return None

        def login(self, username, password):
            return None

        def send_message(self, message):
            self.sent = message

    fake = FakeSMTP()
    monkeypatch.setattr(email_tools.smtplib, "SMTP", lambda *args, **kwargs: fake)
    monkeypatch.setattr(
        email_tools,
        "settings",
        SimpleNamespace(
            SMTP_HOST="smtp.example.com",
            SMTP_PORT=587,
            SMTP_USERNAME="user",
            SMTP_PASSWORD="pass",
            SMTP_FROM_EMAIL="suvyon@example.com",
        ),
    )

    result = email_tools.send_email(
        "ada@example.com",
        "Meeting",
        "See you at 3.",
        user_content="send it",
    )
    assert "sent successfully" in result
    assert fake.sent["To"] == "ada@example.com"
    assert fake.sent["Subject"] == "Meeting"


def test_gmail_app_password_strips_spaces(monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def ehlo(self):
            return None

        def starttls(self):
            return None

        def login(self, username, password):
            captured["user"] = username
            captured["password"] = password

        def send_message(self, message):
            captured["sent"] = True

    monkeypatch.setattr(email_tools.smtplib, "SMTP", lambda *args, **kwargs: FakeSMTP())
    monkeypatch.setattr(email_tools.smtplib, "SMTP_SSL", lambda *args, **kwargs: FakeSMTP())
    monkeypatch.setattr(
        email_tools,
        "settings",
        SimpleNamespace(
            SMTP_HOST="smtp.gmail.com",
            SMTP_PORT=587,
            SMTP_USERNAME="you@gmail.com",
            SMTP_PASSWORD="abcd efgh ijkl mnop",
            SMTP_FROM_EMAIL="you@gmail.com",
        ),
    )
    result = email_tools.send_email(
        "ada@example.com",
        "Meeting",
        "See you at 3.",
        user_content="send it",
    )
    assert "sent successfully" in result
    assert captured["password"] == "abcdefghijklmnop"
    assert email_tools.app_password("abcd efgh ijkl mnop") == "abcdefghijklmnop"
    assert email_tools.app_password('"abcdefghijklmnop"') == "abcdefghijklmnop"
    assert email_tools.user_confirmed_send("send now")


def test_smtp_timeout_mentions_render_block():
    hint = email_tools._smtp_error_hint("timed out")
    assert "Render" in hint
    assert "RESEND_API_KEY" in hint


def test_send_email_uses_resend_over_https(monkeypatch):
    captured = {}

    class FakeResponse:
        status_code = 200
        text = '{"id":"ok"}'

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return FakeResponse()

    monkeypatch.setattr(email_tools.httpx, "post", fake_post)
    monkeypatch.setattr(email_tools.smtplib, "SMTP", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("SMTP must not run")))
    monkeypatch.setattr(
        email_tools,
        "settings",
        SimpleNamespace(
            SMTP_HOST="smtp.gmail.com",
            SMTP_PORT=587,
            SMTP_USERNAME="you@gmail.com",
            SMTP_PASSWORD="abcdefghijklmnop",
            SMTP_FROM_EMAIL="you@gmail.com",
            RESEND_API_KEY="re_test",
            SENDGRID_API_KEY="",
        ),
    )
    result = email_tools.send_email(
        "ada@example.com",
        "Meeting",
        "See you at 3.",
        user_content="send it",
    )
    assert "sent successfully" in result
    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["json"]["to"] == ["ada@example.com"]


def test_approved_email_appends_edited_regards(monkeypatch):
    captured = {}

    def fake_deliver(to, subject, body):
        captured.update(to=to, subject=subject, body=body)

    monkeypatch.setattr(email_tools, "_deliver_email", fake_deliver)
    result = email_tools.send_approved_email(
        "ada@example.com",
        "Meeting",
        "See you at 3.",
        "Regards,\nSujoy",
    )
    assert "sent successfully" in result
    assert captured["body"] == "See you at 3.\n\nRegards,\nSujoy"
