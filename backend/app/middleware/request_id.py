from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Adds a unique request ID to every incoming request.

    The request ID is available through:

    request.state.request_id

    and is also returned to the client as:

    X-Request-ID
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response
