from collections.abc import Iterator

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.agent import Agent
from app.tools.registry import get_tool, get_tool_schemas, list_tools

MAX_ITERATIONS = 4

_TOOL_SYSTEM_SUFFIX = (
    "\n\nYou have tools available. For questions about current events, prices, rates, "
    "scores, weather, news, or anything that requires up-to-date information, you MUST "
    "call the web_search tool before answering. After receiving tool results, answer "
    "with concrete facts from those results and cite source URLs. Do not claim you cannot "
    "access real-time data when tool results are available."
)

_EMAIL_SYSTEM_SUFFIX = (
    "\n\nYou can prepare email drafts. For any request to write, edit, or send a message, "
    "call draft_email with to, subject, and body. The application will show an editable "
    "approval card. Never call send_email and never claim an email was sent; only the "
    "user-facing approval dialog can authorize delivery."
)

_STUDIO_SYSTEM_SUFFIX = (
    "\n\nYou have creative tools. For pictures, call generate_image and include the markdown "
    "image in your reply. If the user asks for a video, clip, or trailer, call "
    "generate_storyboard (paid text-to-video APIs are not used). For voiceover, call "
    "generate_speech. Keep [[suvyon:storyboard]] and [[suvyon:speak]] markers intact."
)

_SYNTHESIZE_PROMPT = (
    "Using the tool results above, answer the user's request now. "
    "Extract concrete facts from those results. Cite source URLs when present. "
    "If an email was drafted but not sent, show the draft and ask for confirmation. "
    "If images, storyboards, QR codes, diagrams, or weather cards were generated, include their markdown "
    "and keep any [[suvyon:...]] markers unchanged. Cite web sources as Markdown links [title](url). "
    "Reply in Markdown, never HTML. "
    "Do not call tools again."
)

_WEB_HINTS = (
    "latest",
    "news",
    "today",
    "current",
    "recent",
    "price",
    "rate",
    "score",
    "weather",
    "stock",
    "gold",
    "live",
    "who won",
    "match",
    "test",
    "innings",
)


def _get_agent_tools(agent: Agent) -> list[str]:
    if not agent.tools:
        return []
    names = [t.strip() for t in agent.tools.split(",") if t.strip()]
    available = list_tools()
    return [n for n in names if n in available]


def _needs_web_search(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in _WEB_HINTS)


def _build_messages(agent: Agent, history: list[dict], user_content: str) -> list[LLMMessage]:
    instructions = agent.instructions or "You are a helpful assistant."
    tool_names = _get_agent_tools(agent)
    if "web_search" in tool_names:
        instructions = instructions.rstrip() + _TOOL_SYSTEM_SUFFIX
    if "draft_email" in tool_names or "send_email" in tool_names:
        instructions = instructions.rstrip() + _EMAIL_SYSTEM_SUFFIX
    if any(name in tool_names for name in ("generate_image", "generate_storyboard", "generate_speech")):
        instructions = instructions.rstrip() + _STUDIO_SYSTEM_SUFFIX

    messages = [LLMMessage(role="system", content=instructions)]
    for h in history:
        if isinstance(h, dict):
            role, content = h.get("role"), h.get("content")
        else:
            role, content = getattr(h, "role", None), getattr(h, "content", None)
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        messages.append(LLMMessage(role=role, content=content))
    messages.append(LLMMessage(role="user", content=user_content))
    return messages


def _normalize_arguments(arguments) -> dict:
    if arguments is None:
        return {}
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        import json

        try:
            parsed = json.loads(arguments)
            return parsed if isinstance(parsed, dict) else {"query": arguments}
        except json.JSONDecodeError:
            return {"query": arguments}
    return {}


def _call_tool(name: str, arguments, *, user_content: str = "") -> str:
    tool = get_tool(name)
    if not tool:
        return f"Unknown tool: {name}"

    args = _normalize_arguments(arguments)
    fn = tool["fn"]

    if name in {"draft_email", "send_email"}:
        to = str(args.get("to") or args.get("recipient") or args.get("email") or "").strip()
        subject = str(args.get("subject") or args.get("title") or "").strip()
        body = str(args.get("body") or args.get("message") or args.get("content") or "").strip()
        try:
            if name == "send_email":
                draft_tool = get_tool("draft_email")
                draft_result = draft_tool["fn"](to=to, subject=subject, body=body)
                return (
                    "BLOCKED: Email was not sent. Review and approve the editable "
                    f"email card in Suvyon.\n\n{draft_result}"
                )
            return fn(to=to, subject=subject, body=body)
        except Exception as exc:
            return f"Tool error: {exc}"

    if name == "generate_image":
        prompt = str(
            args.get("prompt")
            or args.get("description")
            or args.get("text")
            or args.get("query")
            or args.get("image_prompt")
            or user_content
            or ""
        ).strip()
        aspect = str(args.get("aspect") or "square").strip() or "square"
        if not prompt:
            return "Tool error: generate_image requires a prompt."
        try:
            return fn(prompt, aspect=aspect)
        except Exception as exc:
            return f"Tool error: {exc}"

    if name == "web_search":
        query = (
            args.get("query")
            or args.get("q")
            or args.get("search")
            or args.get("text")
            or ""
        )
        if not str(query).strip():
            return "Tool error: web_search requires a query."
        try:
            return fn(str(query).strip())
        except Exception as exc:
            return f"Tool error: {exc}"

    try:
        return fn(**args)
    except TypeError:
        # Models often add extra keys; keep only known parameter names.
        allowed = tool.get("parameters") or {}
        filtered = {k: v for k, v in args.items() if k in allowed}
        try:
            return fn(**filtered) if allowed else fn()
        except Exception as exc:
            return f"Tool error: {exc}"
    except Exception as exc:
        return f"Tool error: {exc}"


def _execute_tool_calls(
    messages: list[LLMMessage],
    tool_calls: list[dict],
    *,
    user_content: str = "",
    pending_email: list[dict] | None = None,
) -> list[str]:
    messages.append(LLMMessage(role="assistant", content="", tool_calls=tool_calls))
    results: list[str] = []
    for call in tool_calls:
        if call.get("name") in {"draft_email", "send_email"} and pending_email is not None:
            args = _normalize_arguments(call.get("arguments"))
            to = str(args.get("to") or args.get("recipient") or args.get("email") or "").strip()
            subject = str(args.get("subject") or args.get("title") or "").strip()
            body = str(args.get("body") or args.get("message") or args.get("content") or "").strip()
            if to and subject and body:
                pending_email[:] = [{"to": to, "subject": subject, "body": body, "regards": ""}]
        result = _call_tool(call["name"], call.get("arguments"), user_content=user_content)
        results.append(result)
        messages.append(
            LLMMessage(
                role="tool",
                content=str(result),
                tool_call_id=call.get("id"),
                name=call["name"],
            )
        )
    return results


def _has_tool_results(messages: list[LLMMessage]) -> bool:
    return any(m.role == "tool" for m in messages)


def _fallback_from_tool_results(results: list[str], user_content: str) -> str:
    usable = [
        r
        for r in results
        if r and not r.startswith("Tool error:") and not r.startswith("Unknown tool:")
    ]
    if not usable:
        joined = "\n\n".join(results).strip()
        return joined or "The tools did not return usable results."
    return f"Here is what the tools returned for “{user_content}”:\n\n" + "\n\n".join(usable)


def _synthesize_answer(
    messages: list[LLMMessage],
    agent: Agent,
    tool_results: list[str],
    user_content: str,
    *,
    provider_name: str | None = None,
    model_id: str | None = None,
) -> str:
    """Ask the model for a final answer with tools disabled so it cannot loop."""
    synth_messages = [
        *messages,
        LLMMessage(role="user", content=_SYNTHESIZE_PROMPT),
    ]
    try:
        response = route_chat(
            synth_messages,
            provider_name=provider_name or agent.provider,
            model_id=model_id or agent.model,
        )
        if (response.content or "").strip():
            return response.content
    except Exception:
        pass
    return _fallback_from_tool_results(tool_results, user_content)


def run_agent(
    agent: Agent,
    user_content: str,
    history: list[dict] | None = None,
    *,
    pending_email: list[dict] | None = None,
) -> str:
    """Run agent with ReAct tool-calling loop. Returns final response."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)
    collected_results: list[str] = []

    for _ in range(MAX_ITERATIONS):
        # Once a tool has run, stop offering tools and write the answer.
        if collected_results:
            return _synthesize_answer(messages, agent, collected_results, user_content)

        response = route_chat(
            messages,
            provider_name=agent.provider,
            model_id=agent.model,
            tools=tool_schemas or None,
        )

        if response.tool_calls:
            collected_results.extend(
                _execute_tool_calls(
                    messages,
                    response.tool_calls,
                    user_content=user_content,
                    pending_email=pending_email,
                )
            )
            return _synthesize_answer(
                messages,
                agent,
                collected_results,
                user_content,
                provider_name=response.provider,
                model_id=response.model,
            )

        if (
            not collected_results
            and "web_search" in tool_names
            and _needs_web_search(user_content)
        ):
            collected_results.extend(
                _execute_tool_calls(
                    messages,
                    [
                        {
                            "id": "forced_web_search",
                            "name": "web_search",
                            "arguments": {"query": user_content},
                        }
                    ],
                    user_content=user_content,
                    pending_email=pending_email,
                )
            )
            return _synthesize_answer(
                messages,
                agent,
                collected_results,
                user_content,
                provider_name=response.provider,
                model_id=response.model,
            )

        if (response.content or "").strip():
            return response.content
        break

    if collected_results:
        return _synthesize_answer(messages, agent, collected_results, user_content)
    return "I could not produce an answer. Please try again."


def stream_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> Iterator[str]:
    """Resolve tool calls first, then stream the final answer."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)
    collected_results: list[str] = []
    pin_provider = agent.provider
    pin_model = agent.model

    if tool_schemas:
        response = route_chat(
            messages,
            provider_name=agent.provider,
            model_id=agent.model,
            tools=tool_schemas,
        )
        pin_provider = response.provider
        pin_model = response.model
        if response.tool_calls:
            collected_results.extend(
                _execute_tool_calls(
                    messages, response.tool_calls, user_content=user_content
                )
            )
        elif "web_search" in tool_names and _needs_web_search(user_content):
            collected_results.extend(
                _execute_tool_calls(
                    messages,
                    [
                        {
                            "id": "forced_web_search",
                            "name": "web_search",
                            "arguments": {"query": user_content},
                        }
                    ],
                    user_content=user_content,
                )
            )
        elif (response.content or "").strip():
            yield response.content
            return

    if collected_results:
        messages.append(LLMMessage(role="user", content=_SYNTHESIZE_PROMPT))

    yielded = False
    for chunk in route_stream(
        messages, provider_name=pin_provider, model_id=pin_model
    ):
        yielded = True
        yield chunk

    if not yielded and collected_results:
        yield _fallback_from_tool_results(collected_results, user_content)
