import json
from collections.abc import Iterator

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo
from app.core.config import settings

_OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

_MODELS = [
    ModelInfo(
        provider="openrouter",
        model_id="meta-llama/llama-3.3-70b-instruct:free",
        display_name="LLaMA 3.3 70B (Free)",
        context_length=131072,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "reasoning"],
    ),
    ModelInfo(
        provider="openrouter",
        model_id="mistralai/mistral-7b-instruct:free",
        display_name="Mistral 7B (Free)",
        context_length=32768,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "fast"],
    ),
    ModelInfo(
        provider="openrouter",
        model_id="google/gemma-3-27b-it:free",
        display_name="Gemma 3 27B (Free)",
        context_length=131072,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat"],
    ),
    ModelInfo(
        provider="openrouter",
        model_id="deepseek/deepseek-r1:free",
        display_name="DeepSeek R1 (Free)",
        context_length=163840,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "reasoning"],
    ),
]


class OpenRouterProvider(BaseLLMProvider):
    provider_name = "openrouter"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://suvyon.app",
            "X-Title": "Suvyon",
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
                f"{_OPENROUTER_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=False, **kwargs),
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )

    def stream(self, messages: list[LLMMessage], model: str, **kwargs) -> Iterator[str]:
        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                f"{_OPENROUTER_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=True, **kwargs),
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

    def list_models(self) -> list[ModelInfo]:
        return _MODELS

    def is_available(self) -> bool:
        return bool(settings.OPENROUTER_API_KEY)
