"""
Document parser.

Extracts plain text from uploaded files.
Supported: PDF, DOCX, TXT, Markdown, CSV.
"""

import csv
import io
from pathlib import Path


def parse(file_path: str, mime_type: str) -> str:
    """Extract plain text from a file. Returns the full text content."""
    path = Path(file_path)

    if mime_type == "application/pdf":
        return _parse_pdf(path)

    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _parse_docx(path)

    if mime_type in ("text/plain", "text/markdown"):
        return path.read_text(encoding="utf-8", errors="ignore")

    if mime_type == "text/csv":
        return _parse_csv(path)

    # Fallback — try reading as plain text
    return path.read_text(encoding="utf-8", errors="ignore")


def _parse_pdf(path: Path) -> str:
    import pymupdf  # fitz

    doc = pymupdf.open(str(path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def _parse_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _parse_csv(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(text))
    rows = [", ".join(row) for row in reader]
    return "\n".join(rows)
