from __future__ import annotations

import base64
import hashlib
import zlib
from datetime import datetime, timezone
from urllib.parse import quote

from app.tools.media import image_url


def qr_code(data: str) -> str:
    """Create a QR code image URL (free public encoder, no key)."""
    payload = (data or "").strip()
    if not payload:
        return "Tool error: qr_code requires text, a URL, or other data."
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=280x280&data={quote(payload)}"
    return f"QR code for: {payload}\n\n![QR code]({url})\n\n{url}"


def draw_diagram(source: str, kind: str = "mermaid") -> str:
    """Render a diagram via Kroki (free public instance, no key)."""
    body = (source or "").strip()
    if not body:
        return "Tool error: draw_diagram requires Mermaid (or similar) source."
    diagram = (kind or "mermaid").strip().lower() or "mermaid"
    digest = base64.urlsafe_b64encode(zlib.compress(body.encode("utf-8"), 9)).decode("ascii")
    url = f"https://kroki.io/{diagram}/svg/{digest}"
    return (
        f"Diagram ({diagram}) rendered.\n\n"
        f"![diagram]({url})\n\n"
        f"Source:\n```{diagram}\n{body}\n```"
    )


def brand_kit(name: str, vibe: str = "") -> str:
    """Invent a free brand kit: palette, voice, and a logo-style image prompt."""
    brand = (name or "").strip()
    if not brand:
        return "Tool error: brand_kit requires a product or brand name."
    mood = (vibe or "modern, confident, human").strip()
    digest = hashlib.sha256(f"{brand}|{mood}".encode()).hexdigest()
    colors = [f"#{digest[i:i + 6]}" for i in range(0, 30, 6)]
    palette = "\n".join(f"- {c}" for c in colors)
    logo = image_url(
        f"minimal vector logo for {brand}, {mood}, flat design, no text, studio lighting",
        aspect="square",
        seed=int(digest[:8], 16),
    )
    poster = image_url(
        f"brand poster for {brand}, {mood}, typography poster, cinematic lighting",
        aspect="portrait",
        seed=int(digest[8:16], 16),
    )
    return (
        f"# Brand kit: {brand}\n"
        f"Voice: {mood}\n\n"
        f"Palette:\n{palette}\n\n"
        f"Tagline seed: {brand} — {mood.split(',')[0].strip()} by design.\n\n"
        f"Logo concept:\n![logo]({logo})\n\n"
        f"Poster concept:\n![poster]({poster})"
    )


def create_event(
    title: str,
    start: str,
    end: str = "",
    location: str = "",
    details: str = "",
) -> str:
    """Build an .ics calendar snippet the user can save (no paid calendar API)."""
    name = (title or "").strip()
    begins = (start or "").strip()
    if not name or not begins:
        return "Tool error: create_event requires title and start (ISO datetime, e.g. 2026-09-01T15:00:00)."

    def _ics_stamp(value: str) -> str:
        cleaned = value.replace("-", "").replace(":", "").replace(" ", "T")
        if "T" not in cleaned:
            cleaned += "T090000"
        if cleaned.endswith("Z"):
            return cleaned
        if len(cleaned) == 15:
            return cleaned
        return cleaned[:15]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dt_start = _ics_stamp(begins)
    dt_end = _ics_stamp(end) if (end or "").strip() else dt_start
    loc = (location or "").replace("\n", " ")
    desc = (details or "").replace("\n", "\\n")
    ics = (
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Suvyon//Calendar//EN\nBEGIN:VEVENT\n"
        f"UID:{hashlib.sha256(name.encode()).hexdigest()[:16]}@suvyon\n"
        f"DTSTAMP:{stamp}\nDTSTART:{dt_start}\nDTEND:{dt_end}\n"
        f"SUMMARY:{name}\nLOCATION:{loc}\nDESCRIPTION:{desc}\n"
        "END:VEVENT\nEND:VCALENDAR\n"
    )
    return (
        f"Calendar event “{name}” is ready. Save the block below as a `.ics` file and open it.\n\n"
        f"```ics\n{ics}```"
    )


def decision_canvas(question: str, options: str, criteria: str = "") -> str:
    """Format a decision matrix the model can score in its reply."""
    q = (question or "").strip()
    if not q:
        return "Tool error: decision_canvas requires a question."
    opts = [part.strip() for part in (options or "").replace(";", ",").split(",") if part.strip()]
    if len(opts) < 2:
        return "Tool error: decision_canvas needs at least two comma-separated options."
    crit = [part.strip() for part in (criteria or "impact, effort, risk, fit").split(",") if part.strip()]
    header = "| Criterion | " + " | ".join(opts) + " | Winner |"
    divider = "| --- | " + " | ".join("---" for _ in opts) + " | --- |"
    rows = [f"| {c} | " + " | ".join("—" for _ in opts) + " | — |" for c in crit]
    return (
        f"Decision canvas for: {q}\n\n"
        f"{header}\n{divider}\n" + "\n".join(rows) + "\n\n"
        "Fill every cell with a 1–5 score and a one-line reason. End with a recommended option "
        "and what would change your mind."
    )
