from fastapi import FastAPI

from app.middleware.cors import register_cors
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware


def register_middleware(application: FastAPI) -> None:
    """
    Register all application middleware.

    Middleware execution order:

    Request
        ↓
    RequestID
        ↓
    Logging
        ↓
    CORS
        ↓
    Route

    Response
        ↑
    """

    application.add_middleware(RequestIDMiddleware)

    application.add_middleware(LoggingMiddleware)

    register_cors(application)
