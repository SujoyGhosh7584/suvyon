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

    def _serialize_tool_calls(self, tool_calls: list[dict]) -> list[dict]:
        """Convert internal tool_calls back to OpenAI wire format."""
        import json

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
            serialized.append(msg)
        payload = {"model": model, "messages": serialized, "stream": stream}
        if "tools" in kwargs and kwargs["tools"]:
            payload["tools"] = kwargs.pop("tools")
        payload.update(kwargs)
        return payload

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{_GROQ_API_URL}/chat/completions",
                headers=self._headers(),
                json=self._build_payload(messages, model, stream=False, **kwargs),
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]["message"]
        usage = data.get("usage", {})

        # Parse tool calls if present
        tool_calls = None
        if choice.get("tool_calls"):
            import json
            tool_calls = [
                {
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"]),
                }
                for tc in choice["tool_calls"]
            ]

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
