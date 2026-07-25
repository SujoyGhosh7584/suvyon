"""
Vector store backed by PostgreSQL + pgvector.

Handles saving embeddings and performing similarity search.
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk, EMBEDDING_DIMENSIONS


def save_chunks(
    session: Session,
    chunks: list[DocumentChunk],
) -> None:
    """Bulk insert document chunks with embeddings."""
    session.add_all(chunks)
    session.flush()


def similarity_search(
    session: Session,
    knowledge_base_id: UUID,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[DocumentChunk]:
    """
    Find the top_k most similar chunks using cosine similarity.
    Requires pgvector extension enabled on the database.
    """
    stmt = text("""
        SELECT id
        FROM document_chunks
        WHERE knowledge_base_id = :kb_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """)

    result = session.execute(
        stmt,
        {
            "kb_id": str(knowledge_base_id),
            "embedding": str(query_embedding),
            "top_k": top_k,
        },
    )

    chunk_ids = [row[0] for row in result]

    if not chunk_ids:
        return []

    return (
        session.query(DocumentChunk)
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )
