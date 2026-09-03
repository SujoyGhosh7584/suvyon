"""
RAG Pipeline.

Orchestrates the full document processing flow:
parse → chunk → embed → store
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus
from app.rag.chunker import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.parser import parse
from app.rag.vector_store import save_chunks

# Batch size for embedding API calls
EMBED_BATCH_SIZE = 50


def process_document(
    session: Session,
    document: Document,
    knowledge_base_id: UUID,
) -> int:
    """
    Process a document through the full RAG pipeline.
    Returns the number of chunks created.
    Updates document status in place.
    """
    document.status = DocumentStatus.PROCESSING.value

    try:
        # 1. Parse
        text = parse(document.file_path, document.mime_type)

        if not text.strip():
            raise ValueError(
                "Document produced no extractable text. If this is a scanned PDF, "
                "run OCR on it before uploading."
            )

        # 2. Chunk
        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("Document produced no chunks after splitting.")

        # 3. Embed in batches
        all_embeddings: list[list[float]] = []
        texts = [c.content for c in chunks]

        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i:i + EMBED_BATCH_SIZE]
            all_embeddings.extend(embed_texts(batch, task_type="RETRIEVAL_DOCUMENT"))

        if len(all_embeddings) != len(chunks):
            raise ValueError(
                f"Embedding count mismatch: {len(all_embeddings)} vectors for {len(chunks)} chunks."
            )

        # 4. Build chunk records
        chunk_records = [
            DocumentChunk(
                document_id=document.id,
                knowledge_base_id=knowledge_base_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, all_embeddings)
        ]

        # 5. Store
        save_chunks(session, chunk_records)

        document.status = DocumentStatus.READY.value
        document.chunk_count = len(chunk_records)
        session.commit()

        return len(chunk_records)

    except Exception as exc:
        session.rollback()
        document.status = DocumentStatus.FAILED.value
        document.error_message = str(exc)
        session.commit()
        raise
