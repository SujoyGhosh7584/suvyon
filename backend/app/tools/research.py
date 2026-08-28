from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import quote

import httpx

_HEADERS = {"User-Agent": "Suvyon/1.0 (research tools; https://github.com)"}


def wikipedia(query: str) -> str:
    """Look up a topic on Wikipedia (free, no key)."""
    q = (query or "").strip()
    if not q:
        return "Tool error: wikipedia requires a query."
    try:
        search = httpx.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": q,
                "utf8": 1,
                "format": "json",
                "srlimit": 3,
            },
            headers=_HEADERS,
            timeout=12,
        )
        search.raise_for_status()
        hits = search.json().get("query", {}).get("search", [])
        if not hits:
            return f"No Wikipedia results for “{q}”."
        title = hits[0].get("title") or q
        slug = quote(title.replace(" ", "_"), safe="")
        summary = httpx.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
            headers=_HEADERS,
            timeout=12,
            follow_redirects=True,
        )
        summary.raise_for_status()
        data = summary.json()
        extract = data.get("extract") or ""
        url = data.get("content_urls", {}).get("desktop", {}).get("page") or data.get("canonicalurl") or ""
        related = "; ".join(h.get("title", "") for h in hits[1:] if h.get("title"))
        extra = f"\nRelated: {related}" if related else ""
        return f"Title: {data.get('title') or title}\nURL: {url}\n{extract}{extra}"
    except Exception as exc:
        return f"Tool error: wikipedia failed ({exc})."


def arxiv_search(query: str) -> str:
    """Search arXiv papers (free, no key)."""
    q = (query or "").strip()
    if not q:
        return "Tool error: arxiv_search requires a query."
    try:
        response = httpx.get(
            "https://export.arxiv.org/api/query",
            params={"search_query": f"all:{q}", "start": 0, "max_results": 5},
            headers=_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = []
        for entry in root.findall("a:entry", ns)[:5]:
            title = " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split())
            summary = " ".join((entry.findtext("a:summary", default="", namespaces=ns) or "").split())
            link = ""
            for el in entry.findall("a:link", ns):
                if el.attrib.get("type") == "application/pdf":
                    link = el.attrib.get("href", "")
                    break
            if not link:
                link = entry.findtext("a:id", default="", namespaces=ns) or ""
            entries.append(f"Title: {title}\nURL: {link}\nAbstract: {summary[:500]}")
        return "\n\n".join(entries) or f"No arXiv papers found for “{q}”."
    except Exception as exc:
        return f"Tool error: arxiv_search failed ({exc})."


def read_page(url: str) -> str:
    """Read a web page as clean text via Jina Reader (free, no key)."""
    target = (url or "").strip()
    if not target.startswith(("http://", "https://")):
        return "Tool error: read_page requires a full http(s) URL."
    try:
        response = httpx.get(
            f"https://r.jina.ai/{target}",
            headers={**_HEADERS, "Accept": "text/plain"},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()
        text = response.text.strip()
        if len(text) > 8000:
            text = text[:8000] + "\n\n[truncated]"
        return text or "The page did not return readable text."
    except Exception as exc:
        return f"Tool error: read_page failed ({exc})."


def tech_pulse(query: str = "") -> str:
    """Hacker News headlines via Algolia (free, no key)."""
    q = (query or "").strip() or "front page"
    try:
        params: dict = {"tags": "story", "hitsPerPage": 8}
        if q.lower() not in {"front page", "frontpage", "top"}:
            params["query"] = q
        else:
            params["query"] = ""
        response = httpx.get(
            "https://hn.algolia.com/api/v1/search",
            params=params,
            headers=_HEADERS,
            timeout=12,
        )
        response.raise_for_status()
        hits = response.json().get("hits", [])
        lines = []
        for hit in hits:
            title = hit.get("title") or ""
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            points = hit.get("points")
            if title:
                lines.append(f"- {title} ({points or 0} pts)\n  {url}")
        return "Hacker News pulse:\n" + ("\n".join(lines) or "No stories found.")
    except Exception as exc:
        return f"Tool error: tech_pulse failed ({exc})."
