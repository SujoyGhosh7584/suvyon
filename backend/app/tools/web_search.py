import httpx

from app.core.config import settings


def _tavily(query: str, max_results: int) -> str:
    response = httpx.post(
        "https://api.tavily.com/search",
        json={"api_key": settings.TAVILY_API_KEY, "query": query, "max_results": max_results},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    formatted = [
        f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}"
        for r in results
    ]
    return "\n\n".join(formatted) or "No results."


def _serper(query: str, max_results: int) -> str:
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": max_results},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json().get("organic", [])
    formatted = [
        f"Title: {r.get('title')}\nURL: {r.get('link')}\nSnippet: {r.get('snippet', '')}"
        for r in items
    ]
    return "\n\n".join(formatted) or "No results."


def _brave(query: str, max_results: int) -> str:
    response = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"Accept": "application/json", "X-Subscription-Token": settings.BRAVE_API_KEY},
        params={"q": query, "count": max_results},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json().get("web", {}).get("results", [])
    formatted = [
        f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('description', '')}"
        for r in items
    ]
    return "\n\n".join(formatted) or "No results."


def _duckduckgo(query: str, max_results: int) -> str:
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        last_error = ""
        backends: list[str | None] = [None, "lite", "html"]
        for backend in backends:
            try:
                kwargs: dict = {"max_results": max_results}
                if backend:
                    kwargs["backend"] = backend
                results = list(DDGS().text(query, **kwargs))
                formatted = [
                    f"Title: {r.get('title')}\nURL: {r.get('href') or r.get('link')}\nSnippet: {r.get('body') or r.get('snippet')}"
                    for r in results
                ]
                joined = "\n\n".join(formatted)
                if joined:
                    return joined
            except Exception as exc:
                last_error = str(exc)
                continue
        instant = _ddg_instant(query)
        if instant:
            return instant
        return f"DuckDuckGo search error: {last_error or 'no results'}"
    except Exception as e:
        instant = _ddg_instant(query)
        if instant:
            return instant
        return f"DuckDuckGo search error: {e}"


def _ddg_instant(query: str) -> str:
    try:
        response = httpx.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        parts: list[str] = []
        if data.get("AbstractText"):
            parts.append(
                f"Title: {data.get('Heading')}\nURL: {data.get('AbstractURL')}\nContent: {data.get('AbstractText')}"
            )
        for topic in data.get("RelatedTopics", [])[:5]:
            if not isinstance(topic, dict):
                continue
            text = topic.get("Text")
            url = topic.get("FirstURL")
            if text:
                parts.append(f"Title: {url or ''}\nURL: {url or ''}\nSnippet: {text}")
        return "\n\n".join(parts)
    except Exception:
        return ""


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using available providers (Tavily → Serper → Brave → DuckDuckGo)."""
    providers = [
        ("tavily", settings.TAVILY_API_KEY, _tavily),
        ("serper", settings.SERPER_API_KEY, _serper),
        ("brave", settings.BRAVE_API_KEY, _brave),
        ("duckduckgo", "free", _duckduckgo),
    ]

    last_error = ""
    for name, key, fn in providers:
        if not key:
            continue
        try:
            res = fn(query, max_results)
            if res and not res.startswith("DuckDuckGo search error"):
                return res
        except Exception as exc:
            last_error = f"{name}: {exc}"
            continue

    return f"Web search could not return results. Details: {last_error}"

