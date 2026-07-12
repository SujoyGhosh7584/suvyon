from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    summary="Health Check",
    description="Returns the current health status of the application.",
)
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Used by:
    - Render health checks
    - Monitoring systems
    - Load balancers
    - Deployment verification
    """

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
