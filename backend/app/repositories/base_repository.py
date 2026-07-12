from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common database operations.

    This class is responsible only for persistence.
    Business rules belong in the service layer.
    """

    model: type[ModelType]

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_by_id(
        self,
        entity_id: UUID,
    ) -> ModelType | None:
        """
        Retrieve an entity by its primary key.
        """

        statement = select(self.model).where(self.model.id == entity_id)

        result = self.session.execute(statement)

        return result.scalar_one_or_none()

    def create(
        self,
        entity: ModelType,
    ) -> ModelType:
        """
        Persist a new entity.
        """

        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)

        return entity

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        """
        Delete an entity.
        """

        self.session.delete(entity)

    def commit(self) -> None:
        """
        Commit the current transaction.
        """

        self.session.commit()

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        self.session.rollback()
