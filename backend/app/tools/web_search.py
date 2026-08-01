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

        results = list(DDGS().text(query, max_results=max_results))
        formatted = [
            f"Title: {r.get('title')}\nURL: {r.get('href') or r.get('link')}\nSnippet: {r.get('body') or r.get('snippet')}"
            for r in results
        ]
        return "\n\n".join(formatted) or "No results."
    except Exception as e:
        return f"DuckDuckGo search error: {e}"


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

