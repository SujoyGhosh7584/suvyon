"""
Vector store backed by PostgreSQL + pgvector.

Handles saving embeddings and performing similarity search.
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk

# Cosine distance (pgvector <=>). Lower is better; ~0.3-0.5 is typically relevant.
MAX_COSINE_DISTANCE = 0.62


def save_chunks(
    session: Session,
    chunks: list[DocumentChunk],
) -> None:
    """Bulk insert document chunks with embeddings."""
    session.add_all(chunks)
    session.flush()


def _diversify_chunk_ids(
    ranked: list[tuple[UUID, UUID]],
    top_k: int,
) -> list[UUID]:
    """
    Pick up to top_k chunk ids while covering as many documents as possible.

    Strategy:
    1. Take the best chunk from each distinct document (in score order).
    2. Fill remaining slots with the next-best unused chunks by score.
    """
    if not ranked:
        return []

    selected: list[UUID] = []
    selected_set: set[UUID] = set()
    seen_docs: set[UUID] = set()

    # Pass 1 — one best chunk per document
    for chunk_id, document_id in ranked:
        if document_id in seen_docs:
            continue
        selected.append(chunk_id)
        selected_set.add(chunk_id)
        seen_docs.add(document_id)
        if len(selected) >= top_k:
            return selected

    # Pass 2 — fill remaining slots by original rank
    for chunk_id, _document_id in ranked:
        if chunk_id in selected_set:
            continue
        selected.append(chunk_id)
        selected_set.add(chunk_id)
        if len(selected) >= top_k:
            break

    return selected


def similarity_search(
    session: Session,
    knowledge_base_id: UUID,
    query_embedding: list[float],
    top_k: int = 5,
    max_distance: float = MAX_COSINE_DISTANCE,
) -> list[DocumentChunk]:
    """
    Find the top_k most similar chunks using cosine similarity.

    Rank within each document first so later uploads cannot be crowded
    out by a larger first file. Requires pgvector.
    """
    per_doc = max(3, top_k)

    chunk_count = session.execute(
        text(
            "SELECT COUNT(*) FROM document_chunks WHERE knowledge_base_id = :kb_id"
        ),
        {"kb_id": str(knowledge_base_id)},
    ).scalar() or 0

    # IVFFlat is unreliable on tiny collections and can return zero neighbors.
    if chunk_count < 40:
        try:
            session.execute(text("SET LOCAL enable_indexscan = off"))
            session.execute(text("SET LOCAL enable_bitmapscan = off"))
        except Exception:
            pass
    else:
        try:
            session.execute(text("SET LOCAL ivfflat.probes = 10"))
        except Exception:
            pass

    stmt = text("""
        WITH scored AS (
            SELECT id, document_id,
                   embedding <=> CAST(:embedding AS vector) AS dist
            FROM document_chunks
            WHERE knowledge_base_id = :kb_id
        ),
        ranked AS (
            SELECT id, document_id, dist,
                   ROW_NUMBER() OVER (
                       PARTITION BY document_id ORDER BY dist
                   ) AS rn
            FROM scored
        )
        SELECT id, document_id, dist
        FROM ranked
        WHERE rn <= :per_doc
          AND dist <= :max_distance
        ORDER BY dist
        LIMIT :fetch_k
    """)

    result = session.execute(
        stmt,
        {
            "kb_id": str(knowledge_base_id),
            "embedding": str(query_embedding),
            "per_doc": per_doc,
            "max_distance": max_distance,
            "fetch_k": max(top_k * 4, 40),
        },
    )

    ranked = [(row[0], row[1]) for row in result]
    chunk_ids = _diversify_chunk_ids(ranked, top_k)

    if not chunk_ids:
        return []

    chunks = (
        session.query(DocumentChunk)
        .filter(DocumentChunk.id.in_(chunk_ids))
        .all()
    )
    chunk_map = {c.id: c for c in chunks}
    return [chunk_map[cid] for cid in chunk_ids if cid in chunk_map]
