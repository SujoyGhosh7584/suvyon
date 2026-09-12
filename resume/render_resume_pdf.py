"""Render the ATS resume HTML to a selectable-text A4 PDF with PyMuPDF."""

from __future__ import annotations

import re
from pathlib import Path

import fitz


RESUME_DIR = Path(__file__).resolve().parent
HTML_PATH = RESUME_DIR / "Sujoy_Ghosh_GenAI_Resume.html"
CSS_PATH = RESUME_DIR / "ats-resume.css"
PDF_PATH = RESUME_DIR / "Sujoy_Ghosh_GenAI_Resume.pdf"

LINKS = {
    "LinkedIn": "https://www.linkedin.com/in/sujoyghosh7584/",
    "GitHub": "https://github.com/SujoyGhosh7584",
    "Suvyon - Live Application": "https://suvyon-ten.vercel.app",
    "GitHub Repository": "https://github.com/SujoyGhosh7584/suvyon",
    "Live Application": "https://suvyon-ten.vercel.app",
    "OpenAPI": "https://suvyonbackend.onrender.com/docs",
}


def body_from_document(document: str) -> str:
    match = re.search(r"<body[^>]*>(.*?)</body>", document, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError(f"No HTML body found in {HTML_PATH}")
    return match.group(1)


def prevent_ligature_codepoints(fragment: str) -> str:
    """Keep PDF text extraction ASCII-friendly for common f-ligatures."""
    parts = re.split(r"(<[^>]+>)", fragment)
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(
            r"f(?=[fil])",
            "<span class=\"ats-character\">f</span>",
            parts[index],
            flags=re.IGNORECASE,
        )
    return "".join(parts)


def render() -> None:
    html = body_from_document(HTML_PATH.read_text(encoding="utf-8"))
    html = prevent_ligature_codepoints(html)
    css = CSS_PATH.read_text(encoding="utf-8")

    project_marker = '<section id="selected-genai-project"'
    project_start = html.find(project_marker)
    if project_start < 0:
        raise ValueError("Could not find the project section used for the page break")
    page_fragments = (html[:project_start] + "</section>", html[project_start:])

    page = fitz.paper_rect("a4")
    content = fitz.Rect(page.x0 + 36, page.y0 + 31, page.x1 - 36, page.y1 - 31)
    writer = fitz.DocumentWriter(str(PDF_PATH), options="compress")

    for fragment in page_fragments:
        story = fitz.Story(
            html=fragment,
            user_css=css,
            archive=fitz.Archive(str(RESUME_DIR)),
        )
        more = True
        while more:
            device = writer.begin_page(page)
            more, _ = story.place(content)
            story.draw(device)
            writer.end_page()
    writer.close()

    document = fitz.open(PDF_PATH)
    for page_number, page_object in enumerate(document):
        page_text = page_object.get_text()
        for label, uri in LINKS.items():
            if label not in page_text:
                continue
            for rectangle in page_object.search_for(label):
                page_object.insert_link(
                    {
                        "kind": fitz.LINK_URI,
                        "from": rectangle,
                        "uri": uri,
                        "page": page_number,
                    }
                )
    document.set_metadata(
        {
            "title": "Sujoy Ghosh - Generative AI Engineer Resume",
            "author": "Sujoy Ghosh",
            "subject": "Generative AI Engineer, AI Engineer, Agentic AI Engineer",
            "keywords": (
                "Generative AI, LLM, RAG, Agentic AI, Python, FastAPI, "
                "PostgreSQL, pgvector, Azure"
            ),
        }
    )
    document.saveIncr()
    document.close()


if __name__ == "__main__":
    render()
