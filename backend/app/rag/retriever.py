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
Use every relevant detail in the context (roles, dates, companies, skills).
If the context is about a different topic than the question, say the documents do not cover this.

Context:
{context}

Question: {question}"""

# Used when Auto selected RAG: never block a general question just because docs exist.
SOFT_CONTEXT_TEMPLATE = """You may use the following document context if it is clearly relevant to the question.
If the context is about a different topic (for example artisan reports when the user asked for code),
ignore the documents completely and answer from your own knowledge.
Never refuse a general request such as writing code, explanations, or tutorials because the files are unrelated.
Only mention the documents when they actually help answer the question.

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
    max_distance: float | None = None,
) -> tuple[list[str], list[str]]:
    """Retrieve similar chunks and attach their source document labels."""
    query_embedding = embed_query(query)
    kwargs: dict = {"top_k": top_k}
    if max_distance is not None:
        kwargs["max_distance"] = max_distance
    chunks = similarity_search(
        session, knowledge_base_id, query_embedding, **kwargs
    )

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


def build_rag_prompt(context: str, question: str, *, strict: bool = True) -> str:
    """Wrap context and question into the RAG prompt template."""
    template = CONTEXT_TEMPLATE if strict else SOFT_CONTEXT_TEMPLATE
    return template.format(context=context, question=question)
