from collections.abc import Iterator

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo
from app.core.config import settings

_GROQ_API_URL = "https://api.groq.com/openai/v1"

_MODELS = [
    ModelInfo(
        provider="groq",
        model_id="llama-3.3-70b-versatile",
        display_name="LLaMA 3.3 70B",
        context_length=128000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "reasoning"],
    ),
    ModelInfo(
        provider="groq",
        model_id="llama-3.1-8b-instant",
        display_name="LLaMA 3.1 8B Instant",
        context_length=128000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "fast"],
    ),
    ModelInfo(
        provider="groq",
        model_id="gemma2-9b-it",
        display_name="Gemma 2 9B",
        context_length=8192,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat"],
    ),
]


class GroqProvider(BaseLLMProvider):
    provider_name = "groq"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

    def _build_payload(
        self, messages: list[LLMMessage], model: str, stream: bool = False, **kwargs
    ) -> dict:
        return {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": stream,
            **kwargs,
        }

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{_GROQ_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=False, **kwargs),
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice,
            provider=self.provider_name,
            model=model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )

    def stream(self, messages: list[LLMMessage], model: str, **kwargs) -> Iterator[str]:
        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                f"{_GROQ_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=True, **kwargs),
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta

    def list_models(self) -> list[ModelInfo]:
        return _MODELS

    def is_available(self) -> bool:
        return bool(settings.GROQ_API_KEY)
