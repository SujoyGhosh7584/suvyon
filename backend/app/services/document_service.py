import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import ALLOWED_DOCUMENT_TYPES, MAX_FILE_SIZE_MB
from app.models.document import Document, DocumentStatus
from app.rag.pipeline import process_document
from app.repositories.document_repository import DocumentRepository

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        session: Session,
    ) -> None:
        self._repo = document_repository
        self._session = session

    def list_documents(self, *, workspace_id) -> list[Document]:
        return self._repo.get_by_workspace(workspace_id)

    def list_conversation_documents(
        self, *, conversation_id, workspace_id
    ) -> list[Document]:
        return self._repo.get_by_conversation(conversation_id, workspace_id)

    def get_document(self, *, document_id, workspace_id) -> Document | None:
        return self._repo.get_by_id_and_workspace(document_id, workspace_id)

    def upload(
        self,
        *,
        workspace_id,
        knowledge_base_id,
        file: UploadFile,
        conversation_id=None,
    ) -> Document:
        # Validate mime type
        if file.content_type not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError(
                f"Unsupported file type: {file.content_type}. "
                f"Allowed: {', '.join(ALLOWED_DOCUMENT_TYPES)}"
            )

        # Read and validate size
        content = file.file.read()
        size_bytes = len(content)

        if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")

        # Save to disk
        dest_dir = UPLOAD_DIR / str(workspace_id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        safe_original_name = Path(file.filename or "document").name
        file_name = f"{uuid.uuid4()}_{safe_original_name}"
        file_path = dest_dir / file_name

        file_path.write_bytes(content)

        # Create document record
        document = Document(
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            name=safe_original_name,
            file_path=str(file_path),
            mime_type=file.content_type,
            size_bytes=size_bytes,
            status=DocumentStatus.PENDING.value,
        )

        try:
            self._repo.create(document)
            self._repo.commit()
            self._repo.refresh(document)
        except SQLAlchemyError:
            self._repo.rollback()
            file_path.unlink(missing_ok=True)
            raise

        # Process synchronously (Phase 13 moves this to Celery)
        process_document(self._session, document, knowledge_base_id)

        # Delete file after processing — embeddings are stored in DB
        file_path.unlink(missing_ok=True)

        return document

    def delete_document(self, *, document: Document) -> None:
        file_path = Path(document.file_path)
        try:
            self._repo.delete(document)
            self._repo.commit()
            file_path.unlink(missing_ok=True)
        except SQLAlchemyError:
            self._repo.rollback()
            raise
