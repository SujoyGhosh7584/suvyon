from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_api_key_service
from app.api.security import get_current_verified_user
from app.models.user import User
from app.schemas.api_key import ApiKeyProvider, ApiKeyStatus, ApiKeyUpsert
from app.services.api_key_service import ApiKeyService, SUPPORTED_API_KEY_PROVIDERS

router = APIRouter(prefix="/users/me/api-keys", tags=["API Keys"])


@router.get("", response_model=list[ApiKeyStatus])
def list_api_keys(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> list[ApiKeyStatus]:
    saved = {item.provider: item for item in service.list_for_user(current_user.id)}
    return [ApiKeyStatus(provider=provider, configured=provider in saved,
                         hint=saved[provider].key_hint if provider in saved else None)
            for provider in SUPPORTED_API_KEY_PROVIDERS]


@router.put("/{provider}", response_model=ApiKeyStatus)
def save_api_key(
    provider: ApiKeyProvider,
    request: ApiKeyUpsert,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> ApiKeyStatus:
    try:
        item = service.upsert(current_user.id, provider, request.api_key)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return ApiKeyStatus(provider=provider, configured=True, hint=item.key_hint)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    provider: ApiKeyProvider,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> None:
    service.remove(current_user.id, provider)
