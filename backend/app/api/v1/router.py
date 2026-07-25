from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.conversations import router as conversations_router
from app.api.v1.routes.models import router as models_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.workspaces import router as workspace_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspace_router)
api_router.include_router(conversations_router)
api_router.include_router(models_router)
