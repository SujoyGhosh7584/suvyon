from uuid import UUID

from sqlalchemy import select

from app.models.document import Document, DocumentStatus
from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    model = Document

    def get_by_workspace(self, workspace_id: UUID) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_by_id_and_workspace(
        self, document_id: UUID, workspace_id: UUID
    ) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.workspace_id == workspace_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_ready_by_workspace(self, workspace_id: UUID) -> list[Document]:
        stmt = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.status == DocumentStatus.READY,
        )
        return list(self.session.execute(stmt).scalars().all())
