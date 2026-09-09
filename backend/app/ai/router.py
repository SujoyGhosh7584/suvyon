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
from app.ai.registry import allowed_models, get_available_providers, get_provider

# Default model per provider when none is specified
_PROVIDER_DEFAULTS: dict[str, str] = {
    "groq": "openai/gpt-oss-20b",
    "gemini": "gemini-flash-latest",
    "openrouter": "openrouter/free",
}

_TOOL_MODEL_DEFAULTS: dict[str, str] = {
    "groq": "openai/gpt-oss-20b",
    "gemini": "gemini-flash-latest",
    "openrouter": "openrouter/free",
}

def _default_model_for(provider_name: str, *, tools: bool) -> str:
    if tools:
        return _TOOL_MODEL_DEFAULTS.get(
            provider_name, _PROVIDER_DEFAULTS.get(provider_name, "")
        )
    return _PROVIDER_DEFAULTS.get(provider_name, "")


def _allowed_default_for(provider: BaseLLMProvider, *, tools: bool) -> str:
    models = allowed_models(provider)
    configured = _default_model_for(provider.provider_name, tools=tools)
    if any(model.model_id == configured for model in models):
        return configured
    return models[0].model_id if models else ""


def _provider_owns_model(provider: BaseLLMProvider, model_id: str) -> bool:
    return any(m.model_id == model_id for m in allowed_models(provider))


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

    available_providers = get_available_providers()
    if not available_providers:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    if provider_name:
        provider = get_provider(provider_name)
        if not provider or not provider.is_available():
            raise ValueError(f"Selected provider '{provider_name}' is unavailable. Choose another provider or Auto.")
        if model_id:
            if not _provider_owns_model(provider, model_id):
                raise ValueError(f"Selected model '{model_id}' is not available for '{provider_name}' under the current model policy. Choose a listed model.")
            return provider, model_id
        default_model = _allowed_default_for(provider, tools=tools)
        if not default_model:
            raise ValueError("No model is available for the selected provider.")
        return provider, default_model

    if model_id:
        for provider in available_providers:
            if _provider_owns_model(provider, model_id):
                return provider, model_id
        raise ValueError(f"Selected model '{model_id}' is unavailable. Choose a listed model or Auto.")

    provider = available_providers[0]
    default_model = _allowed_default_for(provider, tools=tools)
    if not default_model:
        raise ValueError("No zero-cost model is available.")

    return provider, default_model


def _invoke(provider, messages, model, **kwargs):
    response = provider.chat(messages, model, **kwargs)
    response.routing_model = model
    return response


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
            return _invoke(provider, messages, model, **kwargs)
        except Exception as exc:
            raise RuntimeError(
                f"Selected model {provider.provider_name}/{model} failed. "
                f"No other model was substituted. {exc}"
            ) from exc

    available = get_available_providers()
    if not available:
        raise ValueError("No LLM providers are configured. Please check your API keys in .env.")

    providers_to_try = [
        (p, _allowed_default_for(p, tools=has_tools)) for p in available
    ]

    errors: list[str] = []
    for provider, model in providers_to_try:
        if not model:
            continue
        try:
            return _invoke(provider, messages, model, **kwargs)
        except Exception as exc:
            errors.append(f"{provider.provider_name}/{model}: {exc}")
            continue

    raise RuntimeError("All providers failed. " + " | ".join(errors))


def route_stream(
    messages: list[LLMMessage],
    provider_name: str | None = None,
    model_id: str | None = None,
    metadata: dict | None = None,
    **kwargs,
) -> Iterator[str]:
    """Stream a chat response from the resolved provider."""
    provider, model = _resolve(
        provider_name, model_id, tools=bool(kwargs.get("tools"))
    )
    if metadata is None:
        metadata = {}
    metadata.update(provider=provider.provider_name, model=model)
    yield from provider.stream(messages, model, _metadata=metadata, **kwargs)
