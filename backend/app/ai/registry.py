"""
Model Registry.

Single source of truth for all available providers and models.
No hardcoding anywhere else — always query the registry.
"""

from app.ai.providers.base import BaseLLMProvider, ModelInfo
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.groq import GroqProvider
from app.ai.providers.openrouter import OpenRouterProvider

# All registered providers — add new ones here only
_PROVIDERS: list[BaseLLMProvider] = [
    GroqProvider(),
    OpenRouterProvider(),
    GeminiProvider(),
]


def get_provider(name: str) -> BaseLLMProvider | None:
    """Return a provider by name, or None if not found."""
    for p in _PROVIDERS:
        if p.provider_name == name:
            return p
    return None


def get_available_providers() -> list[BaseLLMProvider]:
    """Return all providers that are configured and available."""
    return [p for p in _PROVIDERS if p.is_available()]


def list_all_models() -> list[ModelInfo]:
    """Return every model from every available provider."""
    models = []
    for provider in get_available_providers():
        models.extend(provider.list_models())
    return models


def list_models_by_provider(provider_name: str) -> list[ModelInfo]:
    provider = get_provider(provider_name)
    if provider is None or not provider.is_available():
        return []
    return provider.list_models()
