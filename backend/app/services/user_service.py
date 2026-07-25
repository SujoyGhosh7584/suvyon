from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdateProfile


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def update_profile(self, *, user: User, data: UserUpdateProfile) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        try:
            self._user_repository.commit()
            return user
        except SQLAlchemyError:
            self._user_repository.rollback()
            raise
