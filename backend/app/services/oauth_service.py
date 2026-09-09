from datetime import datetime, timedelta, timezone
import secrets
from urllib.parse import urlencode
from uuid import UUID

import httpx
from jose import JWTError, jwt

from app.core.config import settings
from app.core.token_blacklist import blacklist_token, is_blacklisted


class OAuthService:
    providers = {"google", "github"}

    def _config(self, provider: str) -> tuple[str, str, str]:
        if provider == "google":
            return settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_REDIRECT_URI
        if provider == "github":
            return settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET, settings.GITHUB_REDIRECT_URI
        raise ValueError("Unsupported OAuth provider.")

    def is_configured(self, provider: str) -> bool:
        return all(value.strip() for value in self._config(provider))

    def authorization(self, provider: str) -> tuple[str, str]:
        client_id, _, redirect_uri = self._config(provider)
        if not self.is_configured(provider):
            raise RuntimeError(f"{provider.title()} login is not configured.")
        nonce = secrets.token_urlsafe(32)
        state = jwt.encode(
            {
                "type": "oauth_state",
                "provider": provider,
                "nonce": nonce,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        if provider == "google":
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "nonce": nonce,
                "prompt": "select_account",
            }
            return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}", state
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}", state

    def validate_state(self, provider: str, state: str, cookie_state: str | None) -> None:
        if not cookie_state or not secrets.compare_digest(state, cookie_state):
            raise ValueError("OAuth state validation failed.")
        try:
            payload = jwt.decode(
                state, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError as exc:
            raise ValueError("OAuth state is invalid or expired.") from exc
        if payload.get("type") != "oauth_state" or payload.get("provider") != provider:
            raise ValueError("OAuth state does not match the provider.")

    def create_exchange_ticket(self, user_id: UUID) -> str:
        return jwt.encode(
            {
                "sub": str(user_id),
                "type": "oauth_exchange",
                "jti": secrets.token_urlsafe(24),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=2),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def consume_exchange_ticket(self, ticket: str) -> UUID:
        try:
            payload = jwt.decode(
                ticket, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "oauth_exchange" or not payload.get("jti"):
                raise JWTError("Invalid OAuth exchange ticket.")
            if is_blacklisted(payload["jti"]):
                raise JWTError("OAuth exchange ticket was already used.")
            user_id = UUID(payload["sub"])
        except (JWTError, KeyError, ValueError) as exc:
            raise ValueError("OAuth exchange ticket is invalid or expired.") from exc
        blacklist_token(payload["jti"])
        return user_id

    def fetch_profile(self, provider: str, code: str) -> dict:
        client_id, client_secret, redirect_uri = self._config(provider)
        if not client_id or not client_secret or not redirect_uri:
            raise RuntimeError(f"{provider.title()} login is not configured.")
        return (
            self._google_profile(code, client_id, client_secret, redirect_uri)
            if provider == "google"
            else self._github_profile(code, client_id, client_secret, redirect_uri)
        )

    def _google_profile(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
        with httpx.Client(timeout=20) as client:
            token = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token.raise_for_status()
            access_token = token.json().get("access_token")
            if not access_token:
                raise ValueError("Google did not return an access token.")
            profile = client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile.raise_for_status()
        data = profile.json()
        if not data.get("email") or not data.get("email_verified"):
            raise ValueError("Google did not return a verified email address.")
        return {
            "provider_user_id": str(data["sub"]),
            "email": data["email"].lower(),
            "full_name": data.get("name") or data["email"].split("@", 1)[0],
            "avatar_url": data.get("picture"),
        }

    def _github_profile(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
        with httpx.Client(timeout=20, headers={"User-Agent": "Suvyon"}) as client:
            token = client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            token.raise_for_status()
            access_token = token.json().get("access_token")
            if not access_token:
                raise ValueError("GitHub did not return an access token.")
            auth = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            profile = client.get("https://api.github.com/user", headers=auth)
            profile.raise_for_status()
            emails = client.get("https://api.github.com/user/emails", headers=auth)
            emails.raise_for_status()
        data = profile.json()
        verified = next(
            (item for item in emails.json() if item.get("primary") and item.get("verified")),
            None,
        ) or next((item for item in emails.json() if item.get("verified")), None)
        email = (verified or {}).get("email")
        if not email:
            raise ValueError("GitHub did not provide a verified email address.")
        return {
            "provider_user_id": str(data["id"]),
            "email": email.lower(),
            "full_name": data.get("name") or data.get("login") or email.split("@", 1)[0],
            "avatar_url": data.get("avatar_url"),
        }
