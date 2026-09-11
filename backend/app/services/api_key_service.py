import base64
import hashlib
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user_api_key import UserApiKey

SUPPORTED_API_KEY_PROVIDERS = (
    "groq", "openrouter", "gemini", "cerebras", "sambanova",
    "huggingface", "mistral", "cohere", "nvidia",
)


def _cipher() -> Fernet:
    secret = settings.CREDENTIAL_ENCRYPTION_KEY or settings.SECRET_KEY
    digest = hashlib.sha256(f"suvyon:user-api-keys:{secret}".encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


class ApiKeyService:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(self, user_id: UUID) -> list[UserApiKey]:
        return list(self.session.scalars(
            select(UserApiKey).where(UserApiKey.user_id == user_id).order_by(UserApiKey.provider)
        ).all())

    def decrypted_for_user(self, user_id: UUID) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in self.list_for_user(user_id):
            try:
                result[item.provider] = _cipher().decrypt(item.encrypted_key.encode()).decode()
            except (InvalidToken, UnicodeDecodeError):
                continue
        return result

    def upsert(self, user_id: UUID, provider: str, api_key: str) -> UserApiKey:
        if provider not in SUPPORTED_API_KEY_PROVIDERS:
            raise ValueError("Unsupported AI provider.")
        value = api_key.strip()
        if len(value) < 8:
            raise ValueError("API key is too short.")
        item = self.session.scalar(select(UserApiKey).where(
            UserApiKey.user_id == user_id, UserApiKey.provider == provider
        ))
        if item is None:
            item = UserApiKey(user_id=user_id, provider=provider, encrypted_key="", key_hint="")
        item.encrypted_key = _cipher().encrypt(value.encode()).decode()
        item.key_hint = f"••••{value[-4:]}"
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def remove(self, user_id: UUID, provider: str) -> None:
        item = self.session.scalar(select(UserApiKey).where(
            UserApiKey.user_id == user_id, UserApiKey.provider == provider
        ))
        if item is not None:
            self.session.delete(item)
            self.session.commit()
