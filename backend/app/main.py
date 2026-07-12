from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import configure_logging, logger
from app.middleware import register_middleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Manage application startup and shutdown lifecycle.
    """

    configure_logging()

    logger.info(
        "Application starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )

    try:
        yield
    finally:
        logger.info(
            "Application shutting down",
            app_name=settings.APP_NAME,
        )


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # Register global exception handlers
    register_exception_handlers(application)

    # Register middleware
    register_middleware(application)

    # Register API routes
    application.include_router(
        api_router,
        prefix=settings.API_V1_PREFIX,
    )

    return application


app = create_application()


@app.get(
    "/",
    tags=["Root"],
    summary="Root Endpoint",
)
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Used to verify that the application is running.
    """

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }
