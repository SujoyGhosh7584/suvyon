"""
Text chunker.

Splits documents into overlapping chunks for embedding.
Uses recursive splitting on paragraph → sentence → word boundaries.
"""

from dataclasses import dataclass

CHUNK_SIZE = 512       # target characters per chunk
CHUNK_OVERLAP = 64     # overlap between consecutive chunks
MIN_CHUNK_SIZE = 50    # discard chunks smaller than this


@dataclass
class Chunk:
    content: str
    chunk_index: int
    page_number: int | None = None


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """Split text into overlapping chunks."""
    raw = _recursive_split(text.strip(), chunk_size)
    chunks = _apply_overlap(raw, overlap)
    return [
        Chunk(content=c, chunk_index=i)
        for i, c in enumerate(chunks)
        if len(c.strip()) >= MIN_CHUNK_SIZE
    ]


def _recursive_split(text: str, size: int) -> list[str]:
    """Split on paragraph → newline → sentence → word boundaries."""
    if len(text) <= size:
        return [text]

    for separator in ["\n\n", "\n", ". ", " "]:
        mid = len(text) // 2
        split_pos = text.rfind(separator, 0, mid + size)
        if split_pos != -1:
            left = text[:split_pos + len(separator)].strip()
            right = text[split_pos + len(separator):].strip()
            if left and right:
                return _recursive_split(left, size) + _recursive_split(right, size)

    # Hard split as last resort
    return [text[i:i + size] for i in range(0, len(text), size)]


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    """Prepend the tail of the previous chunk to each chunk."""
    if overlap == 0 or len(chunks) <= 1:
        return chunks

    result = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        result.append(tail + " " + chunks[i])
    return result
