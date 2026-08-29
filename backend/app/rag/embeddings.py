"""
Embedding provider abstraction.

Generates vector embeddings for text chunks.
Supports Gemini (free) and OpenAI-compatible APIs.
"""

import httpx

from app.core.config import settings

EMBEDDING_DIMENSIONS = 768  # gemini-embedding-001 truncated via outputDimensionality


def _embed_gemini(texts: list[str], *, task_type: str) -> list[list[float]]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={settings.GEMINI_API_KEY}"
    payload = {
        "requests": [
            {
                "model": "models/gemini-embedding-001",
                "content": {"parts": [{"text": t}]},
                "taskType": task_type,
                "outputDimensionality": EMBEDDING_DIMENSIONS,
            }
            for t in texts
        ]
    }
    with httpx.Client(timeout=60) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
    embeddings = [item["values"] for item in response.json()["embeddings"]]
    if len(embeddings) != len(texts):
        raise RuntimeError(
            f"Embedding API returned {len(embeddings)} vectors for {len(texts)} texts."
        )
    return embeddings


def _embed_openai_compatible(
    texts: list[str], base_url: str, api_key: str, model: str
) -> list[list[float]]:
    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{base_url}/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"input": texts, "model": model},
        )
        response.raise_for_status()

    data = response.json()["data"]
    return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]


def embed_texts(
    texts: list[str],
    *,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """
    Embed a list of texts using the best available provider.
    Priority: Gemini → OpenRouter (nomic-embed)
    """
    if settings.GEMINI_API_KEY:
        return _embed_gemini(texts, task_type=task_type)

    if settings.OPENROUTER_API_KEY:
        vectors = _embed_openai_compatible(
            texts,
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            model="nomic-ai/nomic-embed-text-v1.5",
        )
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embedding API returned {len(vectors)} vectors for {len(texts)} texts."
            )
        return vectors

    raise RuntimeError(
        "No embedding provider configured. Set GEMINI_API_KEY or OPENROUTER_API_KEY."
    )


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text], task_type="RETRIEVAL_QUERY")[0]
