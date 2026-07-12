from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class WorkspaceBase(BaseSchema):
    """
    Shared workspace fields.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class WorkspaceCreate(WorkspaceBase):
    """
    Schema for creating a workspace.
    """

    pass


class WorkspaceUpdate(BaseSchema):
    """
    Schema for updating a workspace.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool | None = None


class WorkspaceResponse(WorkspaceBase):
    """
    Schema returned by workspace endpoints.
    """

    id: UUID

    owner_id: UUID

    is_active: bool
