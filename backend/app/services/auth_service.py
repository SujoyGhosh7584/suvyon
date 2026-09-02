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
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.services.otp_service import OtpService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        otp_service: OtpService,
    ) -> None:
        self._user_repository = user_repository
        self._otp_service = otp_service

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

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

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
