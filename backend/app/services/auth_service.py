import secrets

from sqlalchemy.exc import SQLAlchemyError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jti,
    get_subject_from_token,
    hash_password,
    verify_password,
)
from app.core.token_blacklist import blacklist_token
from app.exceptions.auth import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.models.user import User
from app.models.oauth_account import OAuthAccount
from app.repositories.oauth_account_repository import OAuthAccountRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.services.otp_service import OtpService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        otp_service: OtpService,
        oauth_repository: OAuthAccountRepository | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._otp_service = otp_service
        self._oauth = oauth_repository

    def register(self, *, full_name: str, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        if self._user_repository.get_by_email(normalized_email) is not None:
            raise EmailAlreadyExistsError()

        user = User(
            full_name=full_name,
            email=normalized_email,
            hashed_password=hash_password(password),
            is_verified=False,
        )

        try:
            self._user_repository.create(user)
            self._otp_service.send_verification(normalized_email, commit=False)
            self._user_repository.commit()
            self._user_repository.refresh(user)
            return user
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise
        except Exception:
            self._user_repository.rollback()
            raise

    def login(self, *, email: str, password: str) -> TokenResponse:
        user = self._user_repository.get_by_email(email.strip().lower())

        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InactiveUserError()

        return self.issue_tokens(user)

    def issue_tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    def issue_tokens_for_user_id(self, user_id) -> TokenResponse:
        user = self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        return self.issue_tokens(user)

    def oauth_login(self, *, provider: str, profile: dict) -> User:
        if self._oauth is None:
            raise RuntimeError("OAuth account storage is unavailable.")
        provider_user_id = str(profile["provider_user_id"])
        email = str(profile["email"]).strip().lower()
        existing_identity = self._oauth.get_by_identity(provider, provider_user_id)
        if existing_identity:
            user = self._user_repository.get_by_id(existing_identity.user_id)
            if user is None or not user.is_active:
                raise InactiveUserError()
            return user

        user = self._user_repository.get_by_email(email)
        if user is None:
            user = User(
                full_name=profile["full_name"],
                email=email,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                avatar_url=profile.get("avatar_url"),
                is_verified=True,
            )
            self._user_repository.create(user)
        elif not user.is_active:
            raise InactiveUserError()

        linked = self._oauth.get_by_user_provider(user.id, provider)
        if linked and linked.provider_user_id != provider_user_id:
            raise ValueError(f"This Suvyon account is already linked to another {provider} account.")
        if not linked:
            self._oauth.create(
                OAuthAccount(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    email=email,
                )
            )
        user.is_verified = True
        if not user.avatar_url and profile.get("avatar_url"):
            user.avatar_url = profile["avatar_url"]
        try:
            self._user_repository.commit()
            self._user_repository.refresh(user)
            return user
        except Exception:
            self._user_repository.rollback()
            raise

    def refresh(self, *, refresh_token: str) -> TokenResponse:
        from jose import JWTError

        from app.core.token_blacklist import is_blacklisted

        try:
            jti = get_jti(refresh_token)
            if is_blacklisted(jti):
                raise InvalidCredentialsError()

            user_id = get_subject_from_token(refresh_token, expected_type="refresh")
        except JWTError:
            raise InvalidCredentialsError()

        user = self._user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()

        # Rotate: blacklist old refresh token
        blacklist_token(jti)

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    def logout(self, *, access_token: str) -> None:
        from jose import JWTError

        try:
            jti = get_jti(access_token)
            blacklist_token(jti)
        except JWTError:
            pass  # Already invalid — treat as success

    def change_password(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError()

        user.hashed_password = hash_password(new_password)

        try:
            self._user_repository.commit()
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

    def deactivate(self, *, user: User) -> None:
        user.is_active = False

        try:
            self._user_repository.commit()
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise
