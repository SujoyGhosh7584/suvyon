"""
RAG Retriever.

Searches the vector store and builds a context string
to inject into the LLM prompt.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document
from app.rag.embeddings import embed_query
from app.rag.vector_store import similarity_search

CONTEXT_TEMPLATE = """Use the following context from one or more uploaded documents to answer the question.
Cite which document each fact comes from when possible.
If the context does not contain enough information, say so.

Context:
{context}

Question: {question}"""


def retrieve_context(
    session: Session,
    knowledge_base_id: UUID,
    query: str,
    top_k: int = 5,
) -> str:
    """
    Embed the query, find similar chunks, return formatted context string.
    Returns empty string if no chunks found.
    """
    query_embedding = embed_query(query)
    chunks = similarity_search(session, knowledge_base_id, query_embedding, top_k)

    if not chunks:
        return ""

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] {chunk.content.strip()}")

    return "\n\n".join(context_parts)


def retrieve_context_with_sources(
    session: Session,
    knowledge_base_id: UUID,
    query: str,
    top_k: int = 5,
) -> tuple[list[str], list[str]]:
    """Retrieve similar chunks and attach their source document labels."""
    query_embedding = embed_query(query)
    chunks = similarity_search(session, knowledge_base_id, query_embedding, top_k)

    if not chunks:
        return [], []

    context_parts: list[str] = []
    sources: list[str] = []

    for chunk in chunks:
        document = (
            session.query(Document).filter(Document.id == chunk.document_id).first()
        )
        document_name = document.name if document else "unknown document"
        context_parts.append(f"[{document_name}] {chunk.content.strip()}")
        sources.append(document_name)

    return context_parts, sources


def build_rag_prompt(context: str, question: str) -> str:
    """Wrap context and question into the RAG prompt template."""
    return CONTEXT_TEMPLATE.format(context=context, question=question)
