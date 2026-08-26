"""
Text chunker.

Splits documents into overlapping chunks for embedding.
Packs paragraphs sequentially so long resumes become many chunks,
not a single truncated blob.
"""

import re
from dataclasses import dataclass

CHUNK_SIZE = 800       # target characters per chunk
CHUNK_OVERLAP = 150    # overlap between consecutive chunks
MIN_CHUNK_SIZE = 20    # keep short-but-real lines (skills, titles)


@dataclass
class Chunk:
    content: str
    chunk_index: int
    page_number: int | None = None


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Split text into overlapping chunks."""
    cleaned = text.strip()
    if not cleaned:
        return []

    raw = _pack_units(_split_units(cleaned, chunk_size), chunk_size)
    chunks = _apply_overlap(raw, overlap)
    return [
        Chunk(content=c, chunk_index=i)
        for i, c in enumerate(chunks)
        if len(c.strip()) >= MIN_CHUNK_SIZE
    ]


def _split_units(text: str, size: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= size:
            units.append(paragraph)
            continue
        units.extend(_split_long(paragraph, size))
    return units


def _split_long(text: str, size: int) -> list[str]:
    if len(text) <= size:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    packed = _pack_units([s.strip() for s in sentences if s.strip()], size)
    if packed:
        overflow: list[str] = []
        for piece in packed:
            if len(piece) <= size:
                overflow.append(piece)
            else:
                overflow.extend(_split_by_words(piece, size))
        return overflow
    return _split_by_words(text, size)


def _split_by_words(text: str, size: int) -> list[str]:
    words = text.split()
    if not words:
        return [text[i:i + size] for i in range(0, len(text), size)]

    pieces: list[str] = []
    buf: list[str] = []
    length = 0
    for word in words:
        extra = len(word) + (1 if buf else 0)
        if buf and length + extra > size:
            pieces.append(" ".join(buf))
            buf = [word]
            length = len(word)
        else:
            buf.append(word)
            length += extra
    if buf:
        pieces.append(" ".join(buf))
    return pieces


def _pack_units(units: list[str], size: int) -> list[str]:
    packed: list[str] = []
    buf = ""
    for unit in units:
        if len(unit) > size:
            if buf:
                packed.append(buf)
                buf = ""
            packed.extend(_split_by_words(unit, size) if " " in unit else [
                unit[i:i + size] for i in range(0, len(unit), size)
            ])
            continue
        candidate = unit if not buf else f"{buf}\n\n{unit}"
        if len(candidate) <= size:
            buf = candidate
        else:
            packed.append(buf)
            buf = unit
    if buf:
        packed.append(buf)
    return packed


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    """Prepend the tail of the previous chunk to each chunk."""
    if overlap == 0 or len(chunks) <= 1:
        return chunks

    result = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        result.append(tail + " " + chunks[i])
    return result
