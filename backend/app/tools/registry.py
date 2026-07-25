from app.tools.calculator import calculator
from app.tools.datetime_tool import datetime_tool
from app.tools.web_search import web_search

TOOL_REGISTRY: dict[str, dict] = {
    "web_search": {
        "fn": web_search,
        "description": "Search the web for current information.",
        "parameters": {"query": "string"},
    },
    "calculator": {
        "fn": calculator,
        "description": "Evaluate a mathematical expression.",
        "parameters": {"expression": "string"},
    },
    "datetime": {
        "fn": datetime_tool,
        "description": "Get the current date and time.",
        "parameters": {},
    },
}


def get_tool(name: str):
    return TOOL_REGISTRY.get(name)


def list_tools() -> list[str]:
    return list(TOOL_REGISTRY.keys())


def get_tool_schemas(tool_names: list[str]) -> list[dict]:
    """Return LLM-compatible tool schemas for the given tool names."""
    schemas = []
    for name in tool_names:
        tool = TOOL_REGISTRY.get(name)
        if not tool:
            continue
        schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {k: {"type": v} for k, v in tool["parameters"].items()},
                    "required": list(tool["parameters"].keys()),
                },
            },
        })
    return schemas
