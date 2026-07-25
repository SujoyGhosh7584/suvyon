from typing import Annotated

from fastapi import APIRouter, Depends

from app.ai.registry import list_all_models, list_models_by_provider
from app.api.security import get_current_active_user
from app.models.user import User
from app.schemas.base import BaseSchema

router = APIRouter(prefix="/models", tags=["Models"])


class ModelInfoResponse(BaseSchema):
    provider: str
    model_id: str
    display_name: str
    context_length: int
    supports_streaming: bool
    cost_per_1k_input: float
    cost_per_1k_output: float
    capabilities: list[str]


@router.get("", response_model=list[ModelInfoResponse])
def get_all_models(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ModelInfoResponse]:
    """List all models from all available providers."""
    return [ModelInfoResponse(**m.__dict__) for m in list_all_models()]


@router.get("/{provider}", response_model=list[ModelInfoResponse])
def get_models_by_provider(
    provider: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ModelInfoResponse]:
    """List all models for a specific provider."""
    return [
        ModelInfoResponse(**m.__dict__)
        for m in list_models_by_provider(provider)
    ]
