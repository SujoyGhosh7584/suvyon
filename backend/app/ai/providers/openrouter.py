import json
from collections.abc import Iterator

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo
from app.core.config import settings

_OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

_MODELS = [
    ModelInfo(
        provider="openrouter",
        model_id="openrouter/free",
        display_name="OpenRouter Free (auto)",
        context_length=131072,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat"],
    ),
    ModelInfo(
        provider="openrouter",
        model_id="openai/gpt-oss-20b:free",
        display_name="GPT-OSS 20B (Free)",
        context_length=131072,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "fast"],
    ),
    ModelInfo(
        provider="openrouter",
        model_id="nvidia/nemotron-3-nano-30b-a3b:free",
        display_name="Nemotron 3 Nano 30B (Free)",
        context_length=262144,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat"],
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

    def _serialize_tool_calls(self, tool_calls: list[dict]) -> list[dict]:
        """Convert internal tool_calls back to OpenAI wire format."""
        serialized = []
        for tc in tool_calls:
            if "function" in tc:
                serialized.append(tc)
                continue
            args = tc.get("arguments", {})
            serialized.append(
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": args if isinstance(args, str) else json.dumps(args),
                    },
                }
            )
        return serialized

    def _build_payload(
        self, messages: list[LLMMessage], model: str, stream: bool = False, **kwargs
    ) -> dict:
        serialized = []
        for m in messages:
            msg: dict = {"role": m.role, "content": m.content or ""}
            if m.tool_calls:
                msg["tool_calls"] = self._serialize_tool_calls(m.tool_calls)
            if m.tool_call_id:
                msg["tool_call_id"] = m.tool_call_id
            if m.name and m.role == "tool":
                msg["name"] = m.name
            serialized.append(msg)

        payload: dict = {"model": model, "messages": serialized, "stream": stream}
        if "tools" in kwargs and kwargs["tools"]:
            payload["tools"] = kwargs.pop("tools")
        payload.update(kwargs)
        return payload

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{_OPENROUTER_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=False, **kwargs),
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]
        usage = data.get("usage", {})

        tool_calls = None
        if choice.get("tool_calls"):
            tool_calls = []
            for tc in choice["tool_calls"]:
                raw_args = tc["function"]["arguments"]
                if isinstance(raw_args, dict):
                    parsed_args = raw_args
                else:
                    try:
                        parsed_args = json.loads(raw_args or "{}")
                    except json.JSONDecodeError:
                        parsed_args = {}
                tool_calls.append(
                    {
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": parsed_args,
                    }
                )

        return LLMResponse(
            content=choice.get("content") or "",
            provider=self.provider_name,
            model=model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            tool_calls=tool_calls,
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
