from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    """
    Service responsible for workspace operations.
    """

    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
    ) -> None:
        self._workspace_repository = workspace_repository

    def list_workspaces(
        self,
        *,
        owner_id: UUID,
    ) -> list[Workspace]:
        """
        Retrieve all workspaces owned by a user.
        """

        return self._workspace_repository.get_by_owner(
            owner_id,
        )

    def get_workspace(
        self,
        *,
        workspace_id: UUID,
        owner_id: UUID,
    ) -> Workspace | None:
        """
        Retrieve a workspace owned by a user.
        """

        return self._workspace_repository.get_by_id_and_owner(
            workspace_id,
            owner_id,
        )

    def create_workspace(
        self,
        *,
        owner_id: UUID,
        data: WorkspaceCreate,
    ) -> Workspace:
        """
        Create a new workspace.
        """

        workspace = Workspace(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
        )

        try:
            self._workspace_repository.create(
                workspace,
            )

            self._workspace_repository.commit()

            return workspace

        except SQLAlchemyError:
            self._workspace_repository.rollback()
            raise

    def update_workspace(
        self,
        *,
        workspace: Workspace,
        data: WorkspaceUpdate,
    ) -> Workspace:
        """
        Update an existing workspace.
        """

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                workspace,
                field,
                value,
            )

        try:
            self._workspace_repository.commit()

            return workspace

        except SQLAlchemyError:
            self._workspace_repository.rollback()
            raise

    def delete_workspace(
        self,
        *,
        workspace: Workspace,
    ) -> None:
        """
        Delete a workspace.
        """

        try:
            self._workspace_repository.delete(
                workspace,
            )

            self._workspace_repository.commit()

        except SQLAlchemyError:
            self._workspace_repository.rollback()
            raise
