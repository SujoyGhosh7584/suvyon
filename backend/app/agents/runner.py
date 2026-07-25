from collections.abc import Iterator

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.agent import Agent
from app.tools.registry import get_tool, get_tool_schemas, list_tools

MAX_ITERATIONS = 5


def _get_agent_tools(agent: Agent) -> list[str]:
    if not agent.tools:
        return []
    names = [t.strip() for t in agent.tools.split(",") if t.strip()]
    available = list_tools()
    return [n for n in names if n in available]


def _build_messages(agent: Agent, history: list[dict], user_content: str) -> list[LLMMessage]:
    messages = [LLMMessage(role="system", content=agent.instructions or "You are a helpful assistant.")]
    for h in history:
        messages.append(LLMMessage(role=h["role"], content=h["content"]))
    messages.append(LLMMessage(role="user", content=user_content))
    return messages


def run_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> str:
    """Run agent with ReAct tool-calling loop. Returns final response."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)

    for _ in range(MAX_ITERATIONS):
        response = route_chat(
            messages,
            provider_name=agent.provider,
            model_id=agent.model,
            tools=tool_schemas or None,
        )

        if not response.tool_calls:
            return response.content

        messages.append(LLMMessage(role="assistant", content=response.content or "", tool_calls=response.tool_calls))

        for call in response.tool_calls:
            tool = get_tool(call["name"])
            try:
                result = tool["fn"](**call["arguments"]) if tool else f"Unknown tool: {call['name']}"
            except Exception as exc:
                result = f"Tool error: {exc}"
            messages.append(LLMMessage(role="tool", content=str(result), tool_call_id=call["id"]))

    return response.content or "Agent reached maximum iterations without a final answer."


def stream_agent(agent: Agent, user_content: str, history: list[dict] | None = None) -> Iterator[str]:
    """Resolve tool calls first, then stream the final answer."""
    history = history or []
    tool_names = _get_agent_tools(agent)
    tool_schemas = get_tool_schemas(tool_names)
    messages = _build_messages(agent, history, user_content)

    if tool_schemas:
        for _ in range(MAX_ITERATIONS):
            response = route_chat(
                messages,
                provider_name=agent.provider,
                model_id=agent.model,
                tools=tool_schemas,
            )
            if not response.tool_calls:
                break
            messages.append(LLMMessage(role="assistant", content=response.content or "", tool_calls=response.tool_calls))
            for call in response.tool_calls:
                tool = get_tool(call["name"])
                try:
                    result = tool["fn"](**call["arguments"]) if tool else f"Unknown tool: {call['name']}"
                except Exception as exc:
                    result = f"Tool error: {exc}"
                messages.append(LLMMessage(role="tool", content=str(result), tool_call_id=call["id"]))

    yield from route_stream(messages, provider_name=agent.provider, model_id=agent.model)
