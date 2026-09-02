import re
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings

_SMTP_TIMEOUT_SECONDS = 8

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


def _smtp_port_blocked(message: str) -> bool:
    lowered = message.lower()
    return any(
        token in lowered
        for token in (
            "timed out",
            "timeout",
            "10060",
            "10061",
            "unreachable",
            "network is unreachable",
            "connection refused",
            "enetunreach",
            "etimedout",
            "errno 101",
            "errno 110",
            "winerror",
        )
    )


def _smtp_error_hint(message: str) -> str:
    lowered = message.lower()
    if "application-specific" in lowered or "username and password not accepted" in lowered:
        return (
            " For Gmail: enable 2-Step Verification, create an App Password at "
            "https://myaccount.google.com/apppasswords, and paste it into SMTP_PASSWORD "
            "(spaces are removed automatically). SMTP_USERNAME must be the full Gmail address."
        )
    if _smtp_port_blocked(message):
        return (
            " Render's free web service blocks outbound SMTP (ports 25, 465, and 587), "
            "so Gmail SMTP works on your laptop but hangs from the Vercel/Render app. "
            "Drafts still work because they never open SMTP. To send from production: "
            "upgrade the Render instance, or set RESEND_API_KEY or SENDGRID_API_KEY "
            "(HTTPS on port 443)."
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


def send_approved_email(to: str, subject: str, body: str, regards: str = "") -> str:
    """Deliver an email reviewed in the authenticated approval dialog."""
    recipient = _validate_address(to)
    if recipient is None:
        raise SmtpSendError("A valid recipient email is required.")
    subject_text = (subject or "").strip()
    body_text = (body or "").strip()
    regards_text = (regards or "").strip()
    if not subject_text or not body_text:
        raise SmtpSendError("Email subject and body are required.")
    final_body = body_text
    if regards_text:
        final_body = f"{body_text.rstrip()}\n\n{regards_text}"
    _deliver_email(recipient, subject_text, final_body)
    return f'Email sent successfully to {recipient} with subject "{subject_text}".'


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
    if _http_mail_provider():
        return
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


def _http_mail_provider() -> str | None:
    if (getattr(settings, "RESEND_API_KEY", "") or "").strip():
        return "resend"
    if (getattr(settings, "SENDGRID_API_KEY", "") or "").strip():
        return "sendgrid"
    return None


def _from_email() -> str:
    username = (getattr(settings, "SMTP_USERNAME", "") or "").strip().strip('"').strip("'")
    return (getattr(settings, "SMTP_FROM_EMAIL", "") or username).strip().strip('"').strip("'")


def _smtp_credentials() -> tuple[str, int, bool, str, str, str]:
    username = (settings.SMTP_USERNAME or "").strip().strip('"').strip("'")
    from_email = (settings.SMTP_FROM_EMAIL or username).strip().strip('"').strip("'")
    host, port, use_ssl = smtp_connection_settings(username)
    password = app_password(settings.SMTP_PASSWORD or "")
    if not host or not from_email or not password:
        raise SmtpNotConfiguredError(
            "SMTP is not configured. Set SMTP_HOST (or a Gmail SMTP_USERNAME), "
            "SMTP_FROM_EMAIL, and SMTP_PASSWORD. Email was not sent. "
            "On Render free, also set RESEND_API_KEY or SENDGRID_API_KEY because SMTP ports are blocked."
        )
    if username.lower().endswith(("@gmail.com", "@googlemail.com")) and len(password) != 16:
        raise SmtpNotConfiguredError(
            "Gmail SMTP_PASSWORD must be a 16-character App Password "
            "(not your normal Gmail password). Put it in quotes in .env, or remove spaces. "
            f"Loaded length was {len(password)}. Email was not sent."
        )
    return host, port, use_ssl, username, password, from_email


def _deliver_email(recipient: str, subject_text: str, body_text: str) -> None:
    provider = _http_mail_provider()
    if provider == "resend":
        _deliver_resend(recipient, subject_text, body_text)
        return
    if provider == "sendgrid":
        _deliver_sendgrid(recipient, subject_text, body_text)
        return

    host, port, use_ssl, username, password, from_email = _smtp_credentials()

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = recipient
    message["Subject"] = subject_text
    message.set_content(body_text)

    try:
        _smtp_send(host, port, use_ssl, username, password, message)
    except Exception as exc:
        blocked = _smtp_port_blocked(str(exc))
        if not use_ssl and host.lower() == "smtp.gmail.com" and not blocked:
            try:
                _smtp_send(host, 465, True, username, password, message)
                return
            except Exception as ssl_exc:
                hint = _smtp_error_hint(f"{exc} {ssl_exc}")
                raise SmtpSendError(f"{ssl_exc}.{hint}".rstrip(".")) from ssl_exc
        hint = _smtp_error_hint(str(exc))
        raise SmtpSendError(f"{exc}.{hint}".rstrip(".")) from exc


def _deliver_resend(recipient: str, subject_text: str, body_text: str) -> None:
    from_email = _from_email()
    if not from_email:
        raise SmtpNotConfiguredError(
            "RESEND_API_KEY is set but SMTP_FROM_EMAIL (or SMTP_USERNAME) is empty."
        )
    api_key = (settings.RESEND_API_KEY or "").strip()
    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [recipient],
                "subject": subject_text,
                "text": body_text,
            },
            timeout=20,
        )
    except Exception as exc:
        raise SmtpSendError(f"Resend request failed ({exc}).") from exc
    if response.status_code >= 400:
        raise SmtpSendError(f"Resend rejected the send ({response.status_code}): {response.text[:400]}")


def _deliver_sendgrid(recipient: str, subject_text: str, body_text: str) -> None:
    from_email = _from_email()
    if not from_email:
        raise SmtpNotConfiguredError(
            "SENDGRID_API_KEY is set but SMTP_FROM_EMAIL (or SMTP_USERNAME) is empty."
        )
    api_key = (settings.SENDGRID_API_KEY or "").strip()
    try:
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": from_email},
                "subject": subject_text,
                "content": [{"type": "text/plain", "value": body_text}],
            },
            timeout=20,
        )
    except Exception as exc:
        raise SmtpSendError(f"SendGrid request failed ({exc}).") from exc
    if response.status_code >= 400:
        raise SmtpSendError(f"SendGrid rejected the send ({response.status_code}): {response.text[:400]}")


def _smtp_send(
    host: str,
    port: int,
    use_ssl: bool,
    username: str,
    password: str,
    message: EmailMessage,
) -> None:
    client_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with client_cls(host, port, timeout=_SMTP_TIMEOUT_SECONDS) as smtp:
        smtp.ehlo()
        if not use_ssl:
            smtp.starttls()
            smtp.ehlo()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)
