from typing import Annotated
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter(prefix="/media", tags=["Media"])

_ALLOWED_HOSTS = {
    "image.pollinations.ai",
    "pollinations.ai",
}


@router.get("/image")
def proxy_pollinations_image(u: Annotated[str, Query(min_length=12)]) -> Response:
    """Stream a Pollinations image through this server. Nothing is written to disk."""
    parsed = urlparse(u)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or host not in _ALLOWED_HOSTS:
        raise HTTPException(status_code=400, detail="Unsupported image host.")

    try:
        with httpx.Client(timeout=90.0, follow_redirects=True) as client:
            remote = client.get(
                u,
                headers={
                    "User-Agent": "Suvyon/1.0 (image proxy)",
                    "Accept": "image/*,*/*",
                    "Referer": "https://suvyon.app/",
                },
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Image generation timed out. Try again.")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Image fetch failed: {exc}")

    if remote.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Image provider returned {remote.status_code}.",
        )

    content_type = remote.headers.get("content-type", "image/jpeg")
    if "html" in content_type or "json" in content_type:
        raise HTTPException(status_code=502, detail="Image provider did not return an image.")

    return Response(
        content=remote.content,
        media_type=content_type.split(";")[0],
        headers={"Cache-Control": "public, max-age=86400"},
    )
