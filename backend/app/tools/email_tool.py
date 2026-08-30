import re
import smtplib
from email.message import EmailMessage

from app.core.config import settings

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_COMPOSE_HINTS = (
    "write",
    "draft",
    "compose",
    "email to",
    "send an email",
    "send email",
    "mail to",
    "write an email",
)

_CONFIRM_EXACT = {
    "send",
    "yes",
    "y",
    "ok",
    "okay",
    "confirm",
    "approved",
    "go ahead",
}

_CONFIRM_PHRASES = (
    "send it",
    "send this",
    "send now",
    "send the email",
    "yes send",
    "yes, send",
    "please send",
    "go ahead and send",
    "confirm send",
    "looks good, send",
)


def app_password(value: str) -> str:
    """Google App Passwords are shown with spaces; SMTP expects 16 characters.

    Unquoted .env values like SMTP_PASSWORD=abcd efgh ijkl mnop are truncated
    at the first space by dotenv. Quote the value or omit spaces.
    """
    cleaned = (value or "").strip().strip('"').strip("'")
    return "".join(cleaned.split())


def smtp_connection_settings(username: str = "") -> tuple[str, int, bool]:
    host = (settings.SMTP_HOST or "").strip()
    user = (username or settings.SMTP_USERNAME or "").strip().lower()
    if not host and user.endswith(("@gmail.com", "@googlemail.com")):
        host = "smtp.gmail.com"
    port = int(settings.SMTP_PORT or 587)
    if host.lower() == "smtp.gmail.com" and port not in {587, 465}:
        port = 587
    use_ssl = port == 465
    return host, port, use_ssl


def _smtp_error_hint(message: str) -> str:
    lowered = message.lower()
    if "application-specific" in lowered or "username and password not accepted" in lowered:
        return (
            " For Gmail: enable 2-Step Verification, create an App Password at "
            "https://myaccount.google.com/apppasswords, and paste it into SMTP_PASSWORD "
            "(spaces are removed automatically). SMTP_USERNAME must be the full Gmail address."
        )
    return ""


def user_confirmed_send(text: str) -> bool:
    """True only for an explicit send approval, not a compose request."""
    lowered = (text or "").lower().strip()
    if not lowered:
        return False
    if any(hint in lowered for hint in _COMPOSE_HINTS):
        return False
    if lowered in _CONFIRM_EXACT:
        return True
    return any(phrase in lowered for phrase in _CONFIRM_PHRASES)


def format_email_draft(to: str, subject: str, body: str) -> str:
    return (
        "Email draft\n"
        f"To: {to}\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )


def _validate_address(address: str) -> str | None:
    cleaned = (address or "").strip()
    if not cleaned or not _EMAIL_RE.match(cleaned):
        return None
    return cleaned


def draft_email(to: str, subject: str, body: str) -> str:
    """Validate and return a formatted draft. Does not send."""
    recipient = _validate_address(to)
    if recipient is None:
        return "Tool error: draft_email requires a valid recipient email in 'to'."
    subject_text = (subject or "").strip() or "(no subject)"
    body_text = (body or "").strip() or "(empty body)"
    return (
        format_email_draft(recipient, subject_text, body_text)
        + "\n\nThe email has not been sent. Show this draft to the user and wait "
        "for edits or an explicit confirmation such as 'send it'."
    )


def send_email(to: str, subject: str, body: str, user_content: str = "") -> str:
    """Send via SMTP only after the user explicitly confirms."""
    recipient = _validate_address(to)
    if recipient is None:
        return "Tool error: send_email requires a valid recipient email in 'to'."
    subject_text = (subject or "").strip()
    body_text = (body or "").strip()
    if not subject_text or not body_text:
        return "Tool error: send_email requires both subject and body."

    draft = format_email_draft(recipient, subject_text, body_text)
    if not user_confirmed_send(user_content):
        return (
            "BLOCKED: Email was not sent. The user has not explicitly confirmed. "
            "Show the draft and wait for confirmation such as 'send it'.\n\n"
            f"{draft}"
        )

    try:
        _deliver_email(recipient, subject_text, body_text)
    except SmtpNotConfiguredError as exc:
        return f"Tool error: {exc}\n\n{draft}"
    except SmtpSendError as exc:
        return f"Tool error: failed to send email ({exc}).\n\n{draft}"

    return f"Email sent successfully to {recipient} with subject “{subject_text}”."


class SmtpNotConfiguredError(Exception):
    """Raised when transactional email cannot be sent because SMTP is missing."""


class SmtpSendError(Exception):
    """Raised when SMTP is configured but delivery fails."""


def smtp_is_configured() -> bool:
    try:
        require_smtp()
        return True
    except SmtpNotConfiguredError:
        return False


def require_smtp() -> None:
    _smtp_credentials()


def send_system_email(to: str, subject: str, body: str) -> None:
    """Send a transactional message (OTP, etc.) without chat confirmation."""
    recipient = _validate_address(to)
    if recipient is None:
        raise SmtpSendError("A valid recipient email is required.")
    subject_text = (subject or "").strip()
    body_text = (body or "").strip()
    if not subject_text or not body_text:
        raise SmtpSendError("Email subject and body are required.")
    _deliver_email(recipient, subject_text, body_text)


def _smtp_credentials() -> tuple[str, int, bool, str, str, str]:
    username = (settings.SMTP_USERNAME or "").strip().strip('"').strip("'")
    from_email = (settings.SMTP_FROM_EMAIL or username).strip().strip('"').strip("'")
    host, port, use_ssl = smtp_connection_settings(username)
    password = app_password(settings.SMTP_PASSWORD or "")
    if not host or not from_email or not password:
        raise SmtpNotConfiguredError(
            "SMTP is not configured. Set SMTP_HOST (or a Gmail SMTP_USERNAME), "
            "SMTP_FROM_EMAIL, and SMTP_PASSWORD. Email was not sent."
        )
    if username.lower().endswith(("@gmail.com", "@googlemail.com")) and len(password) != 16:
        raise SmtpNotConfiguredError(
            "Gmail SMTP_PASSWORD must be a 16-character App Password "
            "(not your normal Gmail password). Put it in quotes in .env, or remove spaces. "
            f"Loaded length was {len(password)}. Email was not sent."
        )
    return host, port, use_ssl, username, password, from_email


def _deliver_email(recipient: str, subject_text: str, body_text: str) -> None:
    host, port, use_ssl, username, password, from_email = _smtp_credentials()

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = recipient
    message["Subject"] = subject_text
    message.set_content(body_text)

    try:
        _smtp_send(host, port, use_ssl, username, password, message)
    except Exception as exc:
        if not use_ssl and host.lower() == "smtp.gmail.com":
            try:
                _smtp_send(host, 465, True, username, password, message)
                return
            except Exception as ssl_exc:
                hint = _smtp_error_hint(f"{exc} {ssl_exc}")
                raise SmtpSendError(f"{ssl_exc}.{hint}".rstrip(".")) from ssl_exc
        hint = _smtp_error_hint(str(exc))
        raise SmtpSendError(f"{exc}.{hint}".rstrip(".")) from exc


def _smtp_send(
    host: str,
    port: int,
    use_ssl: bool,
    username: str,
    password: str,
    message: EmailMessage,
) -> None:
    client_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with client_cls(host, port, timeout=20) as smtp:
        smtp.ehlo()
        if not use_ssl:
            smtp.starttls()
            smtp.ehlo()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)
