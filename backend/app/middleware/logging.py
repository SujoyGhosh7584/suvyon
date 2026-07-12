from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request and outgoing response.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = perf_counter()

        response = await call_next(request)

        duration_ms = round((perf_counter() - start_time) * 1000, 2)

        logger.info(
            "HTTP Request",
            request_id=getattr(request.state, "request_id", None),
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
        )

        return response
