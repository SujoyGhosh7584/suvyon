import json
import uuid
from collections.abc import Iterator

import httpx

from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMResponse, ModelInfo
from app.core.config import settings

_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"

_MODELS = [
    ModelInfo(
        provider="gemini",
        model_id="gemini-flash-latest",
        display_name="Gemini Flash (Latest)",
        context_length=1048576,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "vision", "fast", "tools"],
    ),
    ModelInfo(
        provider="gemini",
        model_id="gemini-3.5-flash",
        display_name="Gemini 3.5 Flash",
        context_length=1048576,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "vision", "fast", "tools"],
    ),
    ModelInfo(
        provider="gemini",
        model_id="gemini-2.0-flash",
        display_name="Gemini 2.0 Flash",
        context_length=1048576,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "vision", "fast", "tools"],
    ),
    ModelInfo(
        provider="gemini",
        model_id="gemini-3.5-flash-lite",
        display_name="Gemini 3.5 Flash Lite",
        context_length=1048576,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        capabilities=["chat", "fast"],
    ),
]


def _openai_tools_to_gemini(tools: list[dict] | None) -> list[dict] | None:
    """Convert OpenAI-style tool schemas to Gemini functionDeclarations."""
    if not tools:
        return None
    declarations = []
    for tool in tools:
        fn = tool.get("function") if isinstance(tool, dict) else None
        if not fn:
            continue
        decl: dict = {
            "name": fn["name"],
            "description": fn.get("description") or "",
        }
        params = fn.get("parameters")
        if params:
            decl["parameters"] = params
        declarations.append(decl)
    if not declarations:
        return None
    return [{"functionDeclarations": declarations}]


def _to_gemini_messages(messages: list[LLMMessage]) -> tuple[str | None, list[dict]]:
    """Convert LLMMessages to Gemini format, including tool calls/results."""
    system_parts: list[str] = []
    contents: list[dict] = []

    for m in messages:
        if m.role == "system":
            if m.content:
                system_parts.append(m.content)
            continue

        if m.role == "tool":
            fn_response: dict = {
                "name": m.name or "tool",
                "response": {"result": m.content or ""},
            }
            if m.tool_call_id:
                fn_response["id"] = m.tool_call_id
            _append_gemini_content(
                contents,
                {
                    "role": "user",
                    "parts": [{"functionResponse": fn_response}],
                },
            )
            continue

        if m.role == "assistant":
            parts: list[dict] = []
            if m.content:
                parts.append({"text": m.content})
            if m.tool_calls:
                for tc in m.tool_calls:
                    part: dict = {
                        "functionCall": {
                            "name": tc["name"],
                            "args": tc.get("arguments") or {},
                        }
                    }
                    if tc.get("id"):
                        part["functionCall"]["id"] = tc["id"]
                    if tc.get("thought_signature"):
                        part["thoughtSignature"] = tc["thought_signature"]
                    parts.append(part)
            if parts:
                _append_gemini_content(contents, {"role": "model", "parts": parts})
            continue

        # user (and any other role treated as user)
        _append_gemini_content(
            contents, {"role": "user", "parts": [{"text": m.content or ""}]}
        )

    system_prompt = "\n\n".join(system_parts) if system_parts else None
    return system_prompt, contents


def _append_gemini_content(contents: list[dict], item: dict) -> None:
    """Gemini requires alternating user/model roles."""
    if contents and contents[-1]["role"] == item["role"]:
        contents[-1]["parts"].extend(item["parts"])
        return
    contents.append(item)


def _extract_text(parts: list[dict]) -> str:
    texts = []
    for part in parts:
        if part.get("thought"):
            continue
        text = part.get("text")
        if text:
            texts.append(text)
    return "".join(texts)


def _parse_tool_calls(parts: list[dict]) -> list[dict] | None:
    tool_calls = []
    for part in parts:
        fc = part.get("functionCall")
        if not fc:
            continue
        call = {
            "id": fc.get("id") or f"call_{uuid.uuid4().hex[:12]}",
            "name": fc["name"],
            "arguments": fc.get("args") or {},
        }
        signature = part.get("thoughtSignature") or fc.get("thoughtSignature")
        if signature:
            call["thought_signature"] = signature
        tool_calls.append(call)
    return tool_calls or None


class GeminiProvider(BaseLLMProvider):
    provider_name = "gemini"

    def _url(self, model: str, stream: bool = False) -> str:
        action = "streamGenerateContent" if stream else "generateContent"
        suffix = "&alt=sse" if stream else ""
        return f"{_GEMINI_API_URL}/models/{model}:{action}?key={settings.GEMINI_API_KEY}{suffix}"

    def _build_payload(
        self,
        contents: list[dict],
        system_prompt: str | None,
        **kwargs,
    ) -> dict:
        payload: dict = {"contents": contents}
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        tools = _openai_tools_to_gemini(kwargs.pop("tools", None))
        if tools:
            payload["tools"] = tools
            # Encourage the model to call tools when they are relevant
            payload["toolConfig"] = {
                "functionCallingConfig": {"mode": "AUTO"}
            }

        # Ignore unknown OpenAI-style kwargs that Gemini does not accept
        kwargs.pop("tool_choice", None)

        generation_config: dict = {}
        # Prevent thinking-only empty replies on Gemini 2.5/3.x.
        generation_config["thinkingConfig"] = {"thinkingBudget": 0}
        if generation_config:
            payload["generationConfig"] = generation_config
        return payload

    def _post_generate(self, model: str, payload: dict) -> dict:
        with httpx.Client(timeout=60) as client:
            response = client.post(self._url(model), json=payload)
            if response.is_error:
                try:
                    err_json = response.json()
                    err_msg = err_json.get("error", {}).get("message", response.text)
                    raise RuntimeError(f"Gemini API error ({response.status_code}): {err_msg}")
                except Exception as exc:
                    if isinstance(exc, RuntimeError):
                        raise
                    response.raise_for_status()
            return response.json()

    def chat(self, messages: list[LLMMessage], model: str, **kwargs) -> LLMResponse:
        system_prompt, contents = _to_gemini_messages(messages)
        if not contents:
            raise RuntimeError("Gemini request has no conversation contents.")

        payload = self._build_payload(contents, system_prompt, **kwargs)
        try:
            data = self._post_generate(model, payload)
        except RuntimeError as exc:
            message = str(exc).lower()
            if "thinking" in message and "generationConfig" in payload:
                payload = dict(payload)
                gen = dict(payload.get("generationConfig") or {})
                gen.pop("thinkingConfig", None)
                if gen:
                    payload["generationConfig"] = gen
                else:
                    payload.pop("generationConfig", None)
                data = self._post_generate(model, payload)
            else:
                raise

        candidates = data.get("candidates") or []
        if not candidates:
            feedback = data.get("promptFeedback") or {}
            reason = feedback.get("blockReason") or data.get("error") or "empty candidates"
            raise RuntimeError(f"Gemini returned no candidates: {reason}")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        content = _extract_text(parts)
        tool_calls = _parse_tool_calls(parts)
        usage = data.get("usageMetadata", {})
        finish_reason = candidate.get("finishReason")

        if not content and not tool_calls:
            raise RuntimeError(
                f"Gemini returned an empty response (finishReason={finish_reason})."
            )

        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            tool_calls=tool_calls,
        )

    def stream(self, messages: list[LLMMessage], model: str, **kwargs) -> Iterator[str]:
        system_prompt, contents = _to_gemini_messages(messages)
        payload = self._build_payload(contents, system_prompt, **kwargs)

        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                self._url(model, stream=True),
                json=payload,
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
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    if line in ("[", "]", ",", "[DONE]"):
                        continue
                    if line.startswith(","):
                        line = line[1:]
                    try:
                        chunk = json.loads(line)
                        parts = (
                            chunk.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [])
                        )
                        text = _extract_text(parts)
                        if text:
                            yield text
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

    def list_models(self) -> list[ModelInfo]:
        return _MODELS

    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)
