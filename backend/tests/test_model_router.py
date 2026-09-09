"""Router should not send a Groq model id to Gemini."""

import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.providers.base import ModelInfo
from app.ai import router as llm_router


class _FakeProvider:
    def __init__(self, name: str, models: list[str]):
        self.provider_name = name
        self._models = [
            ModelInfo(provider=name, model_id=mid, display_name=mid, context_length=1)
            for mid in models
        ]

    def is_available(self) -> bool:
        return True

    def list_models(self):
        return self._models


def test_resolve_does_not_keep_groq_model_on_gemini(monkeypatch):
    groq = _FakeProvider("groq", ["openai/gpt-oss-20b"])
    gemini = _FakeProvider("gemini", ["gemini-flash-latest"])

    monkeypatch.setattr(
        llm_router,
        "get_available_providers",
        lambda: [groq, gemini],
    )
    monkeypatch.setattr(
        llm_router,
        "get_provider",
        lambda name: groq if name == "groq" else gemini if name == "gemini" else None,
    )

    with pytest.raises(ValueError, match="not available"):
        llm_router._resolve("gemini", "openai/gpt-oss-20b", tools=False)



def test_resolve_rejects_retired_model_instead_of_substituting(monkeypatch):
    groq = _FakeProvider("groq", ["openai/gpt-oss-20b"])
    monkeypatch.setattr(llm_router, "get_available_providers", lambda: [groq])
    monkeypatch.setattr(llm_router, "get_provider", lambda name: groq if name == "groq" else None)

    with pytest.raises(ValueError, match="not available"):
        llm_router._resolve("groq", "llama-3.1-8b-instant", tools=True)


@pytest.mark.parametrize("with_tools", [False, True])
def test_explicit_provider_failure_never_calls_another(monkeypatch, with_tools):
    chosen = _FakeProvider("groq", ["chosen"])
    other = _FakeProvider("gemini", ["other"])
    chosen.chat = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("rate limited"))
    other.chat = lambda *a, **kw: pytest.fail("Explicit choice fell back")
    monkeypatch.setattr(llm_router, "get_available_providers", lambda: [chosen, other])
    monkeypatch.setattr(llm_router, "get_provider", lambda _: chosen)
    with pytest.raises(RuntimeError, match="No other model was substituted"):
        llm_router.route_chat([], provider_name="groq", model_id="chosen", tools=[{}] if with_tools else None)


def test_auto_can_fall_back_and_records_reported_model(monkeypatch):
    from app.ai.providers.base import LLMResponse
    first = _FakeProvider("groq", ["one"])
    second = _FakeProvider("openrouter", ["openrouter/free"])
    first.chat = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("unavailable"))
    second.chat = lambda *a, **kw: LLMResponse(content="ok", provider="openrouter", model="actual/model")
    monkeypatch.setattr(llm_router, "get_available_providers", lambda: [first, second])
    result = llm_router.route_chat([])
    assert result.model == "actual/model"
    assert result.routing_model == "openrouter/free"


def test_unknown_provider_or_model_never_selects_first_available(monkeypatch):
    first = _FakeProvider("groq", ["one"])
    monkeypatch.setattr(llm_router, "get_available_providers", lambda: [first])
    monkeypatch.setattr(llm_router, "get_provider", lambda _: None)
    with pytest.raises(ValueError, match="unavailable"):
        llm_router._resolve("missing", None)
    with pytest.raises(ValueError, match="unavailable"):
        llm_router._resolve(None, "missing")
