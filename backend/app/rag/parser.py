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
    try:
        for page in doc:
            pages.append(_pdf_page_text(page))
    finally:
        doc.close()
    return "\n\n".join(p for p in pages if p.strip())


def _pdf_page_text(page) -> str:
    """Extract page text in visual reading order, including table-like blocks."""
    blocks = page.get_text("blocks") or []
    text_blocks = [
        b for b in blocks if len(b) > 4 and isinstance(b[4], str) and b[4].strip()
    ]
    if text_blocks:
        text_blocks.sort(key=lambda b: (round(b[1] / 12), b[0]))
        text = "\n".join(b[4].strip() for b in text_blocks)
        if text.strip():
            return text

    return (page.get_text("text") or "").strip()


def _parse_docx(path: Path) -> str:
    from docx import Document
    from docx.document import Document as DocxDocument
    from docx.oxml.ns import qn
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    parts: list[str] = []

    def iter_block_items(parent):
        parent_elm = parent.element.body if isinstance(parent, DocxDocument) else parent._tc
        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def table_text(table: Table) -> str:
        rows = []
        for row in table.rows:
            cells = []
            seen: set[str] = set()
            for cell in row.cells:
                value = " ".join(cell.text.split())
                if not value or value in seen:
                    continue
                seen.add(value)
                cells.append(value)
            if cells:
                rows.append(" | ".join(cells))
        return "\n".join(rows)

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                parts.append(text)
        elif isinstance(block, Table):
            text = table_text(block)
            if text:
                parts.append(text)

    # Text boxes / shapes often hold resume sidebars that paragraphs miss.
    for node in doc.element.iter(qn("w:txbxContent")):
        texts = [t.text.strip() for t in node.iter(qn("w:t")) if t.text and t.text.strip()]
        joined = " ".join(texts)
        if joined and joined not in parts:
            parts.append(joined)

    return "\n".join(parts)


def _parse_csv(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(text))
    rows = [", ".join(row) for row in reader]
    return "\n".join(rows)
