"""
LLM Router.

Resolves which provider and model to use for a request.
Supports explicit selection, auto-routing, and failover.

Priority:
  1. Explicit provider + model from request
  2. Conversation-level default
  3. Auto: first available provider's default model
"""

from collections.abc import Iterator

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.ai.registry import get_available_providers, get_provider

# Default model per provider when none is specified
_PROVIDER_DEFAULTS: dict[str, str] = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
    # openrouter/free auto-picks a currently available free model
    "openrouter": "openrouter/free",
}


def _resolve(
    provider_name: str | None,
    model_id: str | None,
) -> tuple[BaseLLMProvider, str]:
    """
    Resolve a (provider, model) pair intelligently.
    - If model_id is provided, match against known providers if provider_name is absent/mismatched.
    - Fall back to available providers if specified provider is not configured.
    """
    provider_name = provider_name.strip() if provider_name else None
    model_id = model_id.strip() if model_id else None

    # If model_id is supplied, check if any available provider has this model_id
    available_providers = get_available_providers()
    if not available_providers:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    if model_id:
        # Check if provider_name matches and is available
        if provider_name:
            provider = get_provider(provider_name)
            if provider and provider.is_available():
                return provider, model_id

        # Auto-match provider by model_id
        for p in available_providers:
            model_ids = [m.model_id for m in p.list_models()]
            if model_id in model_ids:
                return p, model_id

        # If model_id didn't match directly, try first available provider with model_id
        if provider_name:
            provider = get_provider(provider_name)
            if provider and provider.is_available():
                return provider, model_id

    # If provider_name specified
    if provider_name:
        provider = get_provider(provider_name)
        if provider and provider.is_available():
            default_model = model_id or _PROVIDER_DEFAULTS.get(provider_name, "")
            if not default_model:
                models = provider.list_models()
                if models:
                    default_model = models[0].model_id
            return provider, default_model

    # Auto-select: first available provider
    provider = available_providers[0]
    default_model = model_id or _PROVIDER_DEFAULTS.get(provider.provider_name, "")
    if not default_model:
        models = provider.list_models()
        if models:
            default_model = models[0].model_id

    return provider, default_model


def route_chat(
    messages: list[LLMMessage],
    provider_name: str | None = None,
    model_id: str | None = None,
    **kwargs,
) -> LLMResponse:
    """Send a chat request. Explicit selection strictly targets requested provider."""
    provider_name = provider_name.strip() if provider_name else None
    model_id = model_id.strip() if model_id else None

    # If user explicitly selected a provider or model, strictly try that provider
    if provider_name or model_id:
        provider, model = _resolve(provider_name, model_id)
        try:
            return provider.chat(messages, model, **kwargs)
        except Exception as exc:
            raise RuntimeError(f"Selected provider '{provider.provider_name}' ({model}) failed: {exc}")

    # Auto mode: try available providers with failover
    available = get_available_providers()
    if not available:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    providers_to_try = [
        (p, _PROVIDER_DEFAULTS.get(p.provider_name, "")) for p in available
    ]

    errors: list[str] = []
    for provider, model in providers_to_try:
        try:
            return provider.chat(messages, model, **kwargs)
        except Exception as exc:
            errors.append(f"{provider.provider_name}/{model}: {exc}")
            continue

    raise RuntimeError("All providers failed. " + " | ".join(errors))



def route_stream(
    messages: list[LLMMessage],
    provider_name: str | None = None,
    model_id: str | None = None,
    **kwargs,
) -> Iterator[str]:
    """Stream a chat response from the resolved provider."""
    provider, model = _resolve(provider_name, model_id)
    yield from provider.stream(messages, model, **kwargs)

