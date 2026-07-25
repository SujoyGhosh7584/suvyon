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
    return "\n\n".join(f"{r['title']}\n{r['content']}" for r in results) or "No results."


def _serper(query: str, max_results: int) -> str:
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": max_results},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json().get("organic", [])
    return "\n\n".join(f"{r['title']}\n{r.get('snippet', '')}" for r in items) or "No results."


def _brave(query: str, max_results: int) -> str:
    response = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"Accept": "application/json", "X-Subscription-Token": settings.BRAVE_API_KEY},
        params={"q": query, "count": max_results},
        timeout=10,
    )
    response.raise_for_status()
    items = response.json().get("web", {}).get("results", [])
    return "\n\n".join(f"{r['title']}\n{r.get('description', '')}" for r in items) or "No results."


def _duckduckgo(query: str, max_results: int) -> str:
    from duckduckgo_search import DDGS
    results = list(DDGS().text(query, max_results=max_results))
    return "\n\n".join(f"{r['title']}\n{r['body']}" for r in results) or "No results."


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
            return fn(query, max_results)
        except Exception as exc:
            last_error = f"{name}: {exc}"
            continue

    return f"All search providers failed. Last error: {last_error}"
