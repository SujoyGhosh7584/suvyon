from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class WorkspaceBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class WorkspaceResponse(WorkspaceBase):
    id: UUID
    owner_id: UUID
    is_active: bool
    is_archived: bool
    is_favourite: bool
