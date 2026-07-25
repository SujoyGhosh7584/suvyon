from uuid import UUID

from app.models.document import DocumentStatus
from app.schemas.base import BaseSchema


class DocumentResponse(BaseSchema):
    id: UUID
    workspace_id: UUID
    name: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    chunk_count: int | None
    error_message: str | None
