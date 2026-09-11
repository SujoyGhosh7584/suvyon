"""
Model Registry.

Single source of truth for all available providers and models.
No hardcoding anywhere else — always query the registry.
"""

from app.ai.providers.base import BaseLLMProvider, ModelInfo
from app.ai.providers.free_tier import free_tier_providers
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.ai.providers.openrouter import OpenRouterProvider
from app.core.config import settings

# All registered providers — add new ones here only
_PROVIDERS: list[BaseLLMProvider] = [
    GroqProvider(),
    OpenRouterProvider(),
    GeminiProvider(),
    *free_tier_providers(),
]


def get_provider(name: str) -> BaseLLMProvider | None:
    """Return a provider by name, or None if not found."""
    for p in _PROVIDERS:
        if p.provider_name == name:
            return p
    return None


def get_available_providers(api_keys: dict[str, str] | None = None) -> list[BaseLLMProvider]:
    """Return all providers that are configured and available."""
    keys = api_keys or {}
    user_providers = [p for p in _PROVIDERS if keys.get(p.provider_name)]
    shared_providers = [p for p in _PROVIDERS if not keys.get(p.provider_name) and p.is_available()]
    return [*user_providers, *shared_providers]


def is_model_allowed(model: ModelInfo) -> bool:
    if not settings.ZERO_COST_MODE:
        return True
    return model.cost_per_1k_input == 0 and model.cost_per_1k_output == 0


def allowed_models(provider: BaseLLMProvider) -> list[ModelInfo]:
    return [model for model in provider.list_models() if is_model_allowed(model)]


def list_all_models(api_keys: dict[str, str] | None = None) -> list[ModelInfo]:
    """Return every model from every available provider."""
    models = []
    for provider in get_available_providers(api_keys):
        models.extend(allowed_models(provider))
    return models


def list_models_by_provider(provider_name: str, api_keys: dict[str, str] | None = None) -> list[ModelInfo]:
    provider = get_provider(provider_name)
    if provider is None or not ((api_keys or {}).get(provider_name) or provider.is_available()):
        return []
    return allowed_models(provider)
