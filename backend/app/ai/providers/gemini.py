import json
from collections.abc import Iterator

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo
from app.core.config import settings

_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"

_MODELS = [
    ModelInfo(
        provider="gemini",
        model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        context_length=1048576,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "vision", "fast"],
    ),
    ModelInfo(
        provider="gemini",
        model_id="gemini-1.5-pro",
        display_name="Gemini 1.5 Pro",
        context_length=2097152,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "vision", "reasoning", "long-context"],
    ),
]


def _to_gemini_messages(messages: list[LLMMessage]) -> tuple[str | None, list[dict]]:
    """Convert LLMMessages to Gemini format, extracting system prompt."""
    system_prompt = None
    contents = []

    for m in messages:
        if m.role == "system":
            system_prompt = m.content
        else:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

    return system_prompt, contents


class GeminiProvider(BaseLLMProvider):
    provider_name = "gemini"

    def _url(self, model: str, stream: bool = False) -> str:
        action = "streamGenerateContent" if stream else "generateContent"
        return f"{_GEMINI_API_URL}/models/{model}:{action}?key={settings.GEMINI_API_KEY}"

    def _build_payload(
        self, messages: list[LLMMessage], system_prompt: str | None, **kwargs
    ) -> dict:
        payload: dict = {"contents": messages}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        return payload

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        system_prompt, contents = _to_gemini_messages(messages)

        with httpx.Client(timeout=60) as client:
            response = client.post(
                self._url(model),
                json=self._build_payload(contents, system_prompt),
            )
            if response.is_error:
                try:
                    err_json = response.json()
                    err_msg = err_json.get("error", {}).get("message", response.text)
                    raise RuntimeError(f"Gemini API error ({response.status_code}): {err_msg}")
                except Exception as exc:
                    if isinstance(exc, RuntimeError):
                        raise
                    response.raise_for_status()
            data = response.json()

        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
        )

    def stream(self, messages: list[LLMMessage], model: str, **kwargs) -> Iterator[str]:
        system_prompt, contents = _to_gemini_messages(messages)

        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                self._url(model, stream=True),
                json=self._build_payload(contents, system_prompt),
            ) as response:
                if response.is_error:
                    response.read()
                    try:
                        err_json = response.json()
                        err_msg = err_json.get("error", {}).get("message", response.text)
                        raise RuntimeError(f"Gemini API error ({response.status_code}): {err_msg}")
                    except Exception as exc:
                        if isinstance(exc, RuntimeError):
                            raise
                        response.raise_for_status()
                for line in response.iter_lines():
                    line = line.strip()
                    if not line or line in ("[", "]", ","):
                        continue
                    # Strip leading comma from array items
                    if line.startswith(","):
                        line = line[1:]
                    try:
                        chunk = json.loads(line)
                        text = (
                            chunk.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        if text:
                            yield text
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue


    def list_models(self) -> list[ModelInfo]:
        return _MODELS

    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)
