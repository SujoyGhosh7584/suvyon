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
    "groq": "llama-3.1-8b-instant",
    "gemini": "gemini-flash-latest",
    # openrouter/free auto-picks a currently available free model
    "openrouter": "openrouter/free",
}

# Preferred models when the request includes tools (function calling)
_TOOL_MODEL_DEFAULTS: dict[str, str] = {
    "groq": "llama-3.1-8b-instant",
    "gemini": "gemini-flash-latest",
    "openrouter": "openrouter/free",
}

# Known-bad tool models → safer substitutes for the same provider
_TOOL_MODEL_FALLBACKS: dict[str, str] = {
    "llama-3.3-70b-versatile": "llama-3.1-8b-instant",
    "gemini-2.5-flash": "gemini-flash-latest",
    "gemini-2.5-pro": "gemini-flash-latest",
    "gemini-2.5-flash-lite": "gemini-flash-latest",
}


def _default_model_for(provider_name: str, *, tools: bool) -> str:
    if tools:
        return _TOOL_MODEL_DEFAULTS.get(
            provider_name, _PROVIDER_DEFAULTS.get(provider_name, "")
        )
    return _PROVIDER_DEFAULTS.get(provider_name, "")


def _provider_owns_model(provider: BaseLLMProvider, model_id: str) -> bool:
    return any(m.model_id == model_id for m in provider.list_models())


def _resolve(
    provider_name: str | None,
    model_id: str | None,
    *,
    tools: bool = False,
) -> tuple[BaseLLMProvider, str]:
    """
    Resolve a (provider, model) pair intelligently.
    Never send a model id that belongs to a different provider.
    """
    provider_name = provider_name.strip() if provider_name else None
    model_id = model_id.strip() if model_id else None

    if tools and model_id in _TOOL_MODEL_FALLBACKS:
        model_id = _TOOL_MODEL_FALLBACKS[model_id]

    available_providers = get_available_providers()
    if not available_providers:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    # Explicit provider always wins — do not keep a leftover Groq model id.
    if provider_name:
        provider = get_provider(provider_name)
        if provider and provider.is_available():
            if model_id and _provider_owns_model(provider, model_id):
                return provider, model_id
            default_model = _default_model_for(provider_name, tools=tools)
            if not default_model:
                models = provider.list_models()
                if models:
                    default_model = models[0].model_id
            return provider, default_model

    if model_id:
        for p in available_providers:
            if _provider_owns_model(p, model_id):
                return p, model_id

    provider = available_providers[0]
    default_model = _default_model_for(provider.provider_name, tools=tools)
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
    """Send a chat request. Explicit provider is not silently swapped to Groq."""
    provider_name = provider_name.strip() if provider_name else None
    model_id = model_id.strip() if model_id else None
    has_tools = bool(kwargs.get("tools"))

    if provider_name or model_id:
        provider, model = _resolve(provider_name, model_id, tools=has_tools)
        try:
            return provider.chat(messages, model, **kwargs)
        except Exception as exc:
            if has_tools:
                errors = [f"{provider.provider_name}/{model}: {exc}"]
                for alt in get_available_providers():
                    alt_model = _default_model_for(alt.provider_name, tools=True)
                    if not alt_model or (alt is provider and alt_model == model):
                        continue
                    try:
                        return alt.chat(messages, alt_model, **kwargs)
                    except Exception as alt_exc:
                        errors.append(f"{alt.provider_name}/{alt_model}: {alt_exc}")
                raise RuntimeError(
                    f"Selected provider '{provider.provider_name}' ({model}) failed "
                    "and tool failover exhausted. " + " | ".join(errors)
                )
            raise RuntimeError(
                f"Selected provider '{provider.provider_name}' ({model}) failed: {exc}"
            )

    available = get_available_providers()
    if not available:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    providers_to_try = [
        (p, _default_model_for(p.provider_name, tools=has_tools)) for p in available
    ]

    errors: list[str] = []
    for provider, model in providers_to_try:
        if not model:
            continue
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
    provider, model = _resolve(
        provider_name, model_id, tools=bool(kwargs.get("tools"))
    )
    yield from provider.stream(messages, model, **kwargs)
