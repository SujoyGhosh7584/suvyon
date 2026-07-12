from sqlalchemy import select

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for user-specific database operations.
    """

    model = User

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Retrieve a user by email address.
        """

        statement = select(User).where(User.email == email)

        result = self.session.execute(statement)

        return result.scalar_one_or_none()
