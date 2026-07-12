from uuid import UUID

from sqlalchemy import select

from app.models.workspace import Workspace
from app.repositories.base_repository import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    """
    Repository for workspace-specific database operations.
    """

    model = Workspace

    def get_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Workspace]:
        """
        Retrieve all workspaces owned by a user.
        """

        statement = (
            select(Workspace)
            .where(Workspace.owner_id == owner_id)
            .order_by(Workspace.created_at.desc())
        )

        result = self.session.execute(statement)

        return list(result.scalars().all())

    def get_by_id_and_owner(
        self,
        workspace_id: UUID,
        owner_id: UUID,
    ) -> Workspace | None:
        """
        Retrieve a workspace owned by a specific user.
        """

        statement = select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == owner_id,
        )

        result = self.session.execute(statement)

        return result.scalar_one_or_none()
