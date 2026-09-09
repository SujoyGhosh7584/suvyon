from uuid import UUID

from sqlalchemy import select

from app.models.oauth_account import OAuthAccount
from app.repositories.base_repository import BaseRepository


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    model = OAuthAccount

    def get_by_identity(self, provider: str, provider_user_id: str) -> OAuthAccount | None:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_user_provider(self, user_id: UUID, provider: str) -> OAuthAccount | None:
        stmt = select(OAuthAccount).where(
            OAuthAccount.user_id == user_id,
            OAuthAccount.provider == provider,
        )
        return self.session.execute(stmt).scalar_one_or_none()

