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

_SYNTHESIZE_PROMPT = (
    "Using the tool results above, answer the user's question now. "
    "Extract scores, dates, and other facts. Cite source URLs. "
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

    messages = [LLMMessage(role="system", content=instructions)]
    for h in history:
        messages.append(LLMMessage(role=h["role"], content=h["content"]))
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


def _call_tool(name: str, arguments) -> str:
    tool = get_tool(name)
    if not tool:
        return f"Unknown tool: {name}"

    args = _normalize_arguments(arguments)
    fn = tool["fn"]

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


def _execute_tool_calls(messages: list[LLMMessage], tool_calls: list[dict]) -> list[str]:
    messages.append(LLMMessage(role="assistant", content="", tool_calls=tool_calls))
    results: list[str] = []
    for call in tool_calls:
        result = _call_tool(call["name"], call.get("arguments"))
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
    usable = [r for r in results if r and not r.startswith("Tool error:") and r != "Unknown tool: web_search"]
    if not usable:
        joined = "\n\n".join(results).strip()
        return joined or "Web search did not return usable results."
    return (
        "Here is what web search returned for "
        f"“{user_content}”:\n\n" + "\n\n".join(usable)
    )


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


def run_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> str:
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
            collected_results.extend(_execute_tool_calls(messages, response.tool_calls))
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
            collected_results.extend(_execute_tool_calls(messages, response.tool_calls))
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
