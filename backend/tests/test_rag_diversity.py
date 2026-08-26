"""Unit tests for multi-document RAG diversification."""

import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.vector_store import _diversify_chunk_ids


def test_diversify_prefers_one_chunk_per_document():
    doc_a, doc_b, doc_c = uuid4(), uuid4(), uuid4()
    c1, c2, c3, c4, c5 = uuid4(), uuid4(), uuid4(), uuid4(), uuid4()

    # Ranked by similarity: all of doc_a first, then others
    ranked = [
        (c1, doc_a),
        (c2, doc_a),
        (c3, doc_a),
        (c4, doc_b),
        (c5, doc_c),
    ]

    selected = _diversify_chunk_ids(ranked, top_k=3)
    assert len(selected) == 3
    assert selected[0] == c1  # best from doc_a
    assert selected[1] == c4  # best from doc_b
    assert selected[2] == c5  # best from doc_c


def test_diversify_fills_remaining_slots_by_rank():
    doc_a, doc_b = uuid4(), uuid4()
    c1, c2, c3, c4 = uuid4(), uuid4(), uuid4(), uuid4()
    ranked = [
        (c1, doc_a),
        (c2, doc_a),
        (c3, doc_b),
        (c4, doc_a),
    ]

    selected = _diversify_chunk_ids(ranked, top_k=3)
    assert selected == [c1, c3, c2]
