from collections.abc import Iterator

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.agent import Agent
from app.tools.registry import get_tool, get_tool_schemas, list_tools

MAX_ITERATIONS = 5

_TOOL_SYSTEM_SUFFIX = (
    "\n\nYou have tools available. For questions about current events, prices, rates, "
    "scores, weather, news, or anything that requires up-to-date information, you MUST "
    "call the web_search tool before answering. After receiving tool results, answer "
    "with concrete facts from those results and cite source URLs. Do not claim you cannot "
    "access real-time data when tool results are available."
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


def _execute_tool_calls(messages: list[LLMMessage], tool_calls: list[dict]) -> None:
    messages.append(
        LLMMessage(role="assistant", content="", tool_calls=tool_calls)
    )
    for call in tool_calls:
        tool = get_tool(call["name"])
        args = _normalize_arguments(call.get("arguments"))
        try:
            result = tool["fn"](**args) if tool else f"Unknown tool: {call['name']}"
        except Exception as exc:
            result = f"Tool error: {exc}"
        messages.append(
            LLMMessage(
                role="tool",
                content=str(result),
                tool_call_id=call.get("id"),
                name=call["name"],
            )
        )


def run_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> str:
    """Run agent with ReAct tool-calling loop. Returns final response."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)
    forced_search = False

    response_content = "Agent reached maximum iterations without a final answer."
    for _ in range(MAX_ITERATIONS):
        response = route_chat(
            messages,
            provider_name=agent.provider,
            model_id=agent.model,
            tools=tool_schemas or None,
        )

        if not response.tool_calls:
            if (
                not forced_search
                and "web_search" in tool_names
                and _needs_web_search(user_content)
            ):
                forced_search = True
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
                continue
            return response.content

        _execute_tool_calls(messages, response.tool_calls)
        response_content = response.content or response_content

    return response_content


def stream_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> Iterator[str]:
    """Resolve tool calls first, then stream the final answer."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)
    forced_search = False

    if tool_schemas:
        for _ in range(MAX_ITERATIONS):
            response = route_chat(
                messages,
                provider_name=agent.provider,
                model_id=agent.model,
                tools=tool_schemas,
            )
            if not response.tool_calls:
                if (
                    not forced_search
                    and "web_search" in tool_names
                    and _needs_web_search(user_content)
                ):
                    forced_search = True
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
                    continue
                break
            _execute_tool_calls(messages, response.tool_calls)

    yield from route_stream(messages, provider_name=agent.provider, model_id=agent.model)
