from sqlalchemy.exc import SQLAlchemyError

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.exceptions.auth import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Service responsible for authentication operations.
    """

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    def register(
        self,
        *,
        full_name: str,
        email: str,
        password: str,
    ) -> User:
        """
        Register a new user.
        """

        existing_user = self._user_repository.get_by_email(
            email,
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError()

        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(
                password,
            ),
        )

        try:
            self._user_repository.create(
                user,
            )

            self._user_repository.commit()

            return user

        except SQLAlchemyError:
            self._user_repository.rollback()
            raise

    def login(
        self,
        *,
        email: str,
        password: str,
    ) -> str:
        """
        Authenticate a user and return an access token.
        """

        user = self._user_repository.get_by_email(
            email,
        )

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        return create_access_token(
            str(user.id),
        )
