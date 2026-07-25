"""
RAG Retriever.

Searches the vector store and builds a context string
to inject into the LLM prompt.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.rag.embeddings import embed_query
from app.rag.vector_store import similarity_search

CONTEXT_TEMPLATE = """Use the following context to answer the question.
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


def build_rag_prompt(context: str, question: str) -> str:
    """Wrap context and question into the RAG prompt template."""
    return CONTEXT_TEMPLATE.format(context=context, question=question)
