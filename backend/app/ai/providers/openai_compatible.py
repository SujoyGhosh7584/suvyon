"""Reusable adapter for hosted providers that expose OpenAI Chat Completions."""

import json
from collections.abc import Iterator
from typing import Callable

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, *, name: str, base_url: str, api_key: Callable[[], str],
                 models: list[ModelInfo], extra_headers: dict[str, str] | None = None,
                 system_role: str = "system") -> None:
        self.provider_name = name
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._models = models
        self._extra_headers = extra_headers or {}
        self._system_role = system_role

    def _headers(self, api_key: str | None = None) -> dict[str, str]:
        return {"Authorization": f"Bearer {api_key or self._api_key()}",
                "Content-Type": "application/json", **self._extra_headers}

    @staticmethod
    def _serialize_tool_calls(tool_calls: list[dict]) -> list[dict]:
        result = []
        for call in tool_calls:
            if "function" in call:
                result.append(call)
                continue
            arguments = call.get("arguments", {})
            result.append({"id": call["id"], "type": "function", "function": {
                "name": call["name"],
                "arguments": arguments if isinstance(arguments, str) else json.dumps(arguments),
            }})
        return result

    def _payload(self, messages: list[LLMMessage], model: str, stream: bool, **kwargs) -> dict:
        serialized = []
        for message in messages:
            role = self._system_role if message.role == "system" else message.role
            item: dict = {"role": role, "content": message.content or ""}
            if message.tool_calls:
                item["tool_calls"] = self._serialize_tool_calls(message.tool_calls)
            if message.tool_call_id:
                item["tool_call_id"] = message.tool_call_id
            if message.name and message.role == "tool":
                item["name"] = message.name
            serialized.append(item)
        payload = {"model": model, "messages": serialized, "stream": stream}
        if kwargs.get("tools"):
            payload["tools"] = kwargs.pop("tools")
        payload.update(kwargs)
        return payload

    @staticmethod
    def _tool_calls(message: dict) -> list[dict] | None:
        if not message.get("tool_calls"):
            return None
        result = []
        for call in message["tool_calls"]:
            raw = call.get("function", {}).get("arguments", "{}")
            try:
                arguments = raw if isinstance(raw, dict) else json.loads(raw or "{}")
            except json.JSONDecodeError:
                arguments = {}
            result.append({"id": call.get("id") or "call",
                           "name": call.get("function", {}).get("name") or "",
                           "arguments": arguments})
        return result

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        api_key = kwargs.pop("_api_key", None)
        with httpx.Client(timeout=60) as client:
            response = client.post(f"{self._base_url}/chat/completions",
                                   headers=self._headers(api_key),
                                   json=self._payload(messages, model, False, **kwargs))
        if response.status_code >= 400:
            try:
                detail = response.json().get("error", response.json())
                if isinstance(detail, dict):
                    detail = detail.get("message") or detail.get("detail") or str(detail)
            except Exception:
                detail = response.text
            raise RuntimeError(f"{self.provider_name} API error ({response.status_code}): {detail}")
        data = response.json()
        message = data["choices"][0]["message"]
        usage = data.get("usage", {})
        content = message.get("content") or ""
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return LLMResponse(content=content, provider=self.provider_name,
                           model=data.get("model") or model,
                           prompt_tokens=usage.get("prompt_tokens"),
                           completion_tokens=usage.get("completion_tokens"),
                           tool_calls=self._tool_calls(message))

    def stream(self, messages: list[LLMMessage], model: str, **kwargs) -> Iterator[str]:
        metadata = kwargs.pop("_metadata", None)
        api_key = kwargs.pop("_api_key", None)
        with httpx.Client(timeout=120) as client:
            with client.stream("POST", f"{self._base_url}/chat/completions",
                               headers=self._headers(api_key),
                               json=self._payload(messages, model, True, **kwargs)) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: ") or line == "data: [DONE]":
                        continue
                    try:
                        chunk = json.loads(line[6:])
                        if metadata is not None and chunk.get("model"):
                            metadata["model"] = chunk["model"]
                        content = chunk["choices"][0]["delta"].get("content") or ""
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                        continue

    def list_models(self) -> list[ModelInfo]:
        return self._models

    def is_available(self) -> bool:
        return bool(self._api_key())
