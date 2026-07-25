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
    "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
}


def _resolve(
    provider_name: str | None,
    model_id: str | None,
) -> tuple[BaseLLMProvider, str]:
    """
    Resolve a (provider, model) pair.
    Raises ValueError if no provider is available.
    """
    if provider_name:
        provider = get_provider(provider_name)
        if provider is None or not provider.is_available():
            raise ValueError(f"Provider '{provider_name}' is not available.")
        model = model_id or _PROVIDER_DEFAULTS.get(provider_name, "")
        return provider, model

    # Auto-select: first available provider
    available = get_available_providers()
    if not available:
        raise ValueError("No LLM providers are configured.")

    provider = available[0]
    model = model_id or _PROVIDER_DEFAULTS.get(provider.provider_name, "")
    return provider, model


def route_chat(
    messages: list[LLMMessage],
    provider_name: str | None = None,
    model_id: str | None = None,
    **kwargs,
) -> LLMResponse:
    """Send a chat request, with automatic failover across providers."""
    providers_to_try: list[tuple[BaseLLMProvider, str]] = []

    if provider_name:
        provider, model = _resolve(provider_name, model_id)
        providers_to_try = [(provider, model)]
    else:
        available = get_available_providers()
        if not available:
            raise ValueError("No LLM providers are configured.")
        providers_to_try = [
            (p, _PROVIDER_DEFAULTS.get(p.provider_name, "")) for p in available
        ]

    last_error: Exception | None = None
    for provider, model in providers_to_try:
        try:
            return provider.chat(messages, model, **kwargs)
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def route_stream(
    messages: list[LLMMessage],
    provider_name: str | None = None,
    model_id: str | None = None,
    **kwargs,
) -> Iterator[str]:
    """Stream a chat response from the resolved provider."""
    provider, model = _resolve(provider_name, model_id)
    yield from provider.stream(messages, model, **kwargs)
