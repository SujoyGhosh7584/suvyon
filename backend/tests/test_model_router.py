"""Router should not send a Groq model id to Gemini."""

import sys
from pathlib import Path
from types import SimpleNamespace

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
    groq = _FakeProvider("groq", ["llama-3.1-8b-instant"])
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

    provider, model = llm_router._resolve(
        "gemini",
        "llama-3.1-8b-instant",
        tools=False,
    )
    assert provider.provider_name == "gemini"
    assert model == "gemini-flash-latest"
