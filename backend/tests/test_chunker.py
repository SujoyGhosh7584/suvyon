"""Unit tests for document chunking."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.chunker import chunk_text


def test_chunk_text_splits_long_resume_into_multiple_chunks():
    sections = [
        "SUJOY GHOSH\nSoftware Engineer\nBengaluru, India",
        "WORK EXPERIENCE\n"
        + "Led backend systems, RAG pipelines, and chat routing. " * 40,
        "EDUCATION\nB.Tech in Computer Science from Example University. " * 20,
        "SKILLS\nPython, FastAPI, PostgreSQL, React, TypeScript.",
    ]
    text = "\n\n".join(sections)

    chunks = chunk_text(text)
    assert len(chunks) > 1
    joined = " ".join(c.content for c in chunks)
    assert "WORK EXPERIENCE" in joined
    assert "Led backend systems" in joined
    assert "EDUCATION" in joined


def test_chunk_text_keeps_short_documents():
    chunks = chunk_text("Just a name: Sujoy Ghosh")
    assert len(chunks) == 1
    assert "Sujoy Ghosh" in chunks[0].content
