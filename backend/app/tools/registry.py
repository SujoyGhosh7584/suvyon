from app.tools.calculator import calculator
from app.tools.datetime_tool import datetime_tool
from app.tools.email_tool import draft_email, send_email
from app.tools.media import generate_image, generate_speech, generate_storyboard
from app.tools.research import arxiv_search, read_page, tech_pulse, wikipedia
from app.tools.studio import brand_kit, create_event, decision_canvas, draw_diagram, qr_code
from app.tools.web_search import web_search
from app.tools.world import lookup_place, weather

TOOL_REGISTRY: dict[str, dict] = {
    "web_search": {
        "fn": web_search,
        "description": (
            "Search the live web. Use this instead of memory for news, prices, "
            "sports scores, weather, elections, and who currently holds public office."
        ),
        "parameters": {"query": "string"},
    },
    "generate_image": {
        "fn": generate_image,
        "description": (
            "Generate an AI image from a text prompt using a free public model. "
            "Use for photos, illustrations, logos, product shots, and concept art. "
            "Return the markdown image from the tool result in your reply."
        ),
        "parameters": {"prompt": "string", "aspect": "string"},
        "required": ["prompt"],
    },
    "generate_storyboard": {
        "fn": generate_storyboard,
        "description": (
            "Create a cinematic multi-shot visual sequence (free alternative to paid "
            "text-to-video). Use when the user asks for a video, clip, trailer, or scene."
        ),
        "parameters": {"prompt": "string", "frames": "string"},
        "required": ["prompt"],
    },
    "generate_speech": {
        "fn": generate_speech,
        "description": (
            "Prepare a voiceover the app plays with the device speech engine. "
            "Use for narration, scripts, and read-aloud requests."
        ),
        "parameters": {"text": "string"},
    },
    "wikipedia": {
        "fn": wikipedia,
        "description": (
            "Look up an encyclopedia summary on Wikipedia. Use this for people, "
            "places, and who currently holds a public office instead of guessing."
        ),
        "parameters": {"query": "string"},
    },
    "arxiv_search": {
        "fn": arxiv_search,
        "description": "Search academic papers on arXiv and return titles, links, and abstracts.",
        "parameters": {"query": "string"},
    },
    "read_page": {
        "fn": read_page,
        "description": "Read and extract clean text from a public web page URL.",
        "parameters": {"url": "string"},
    },
    "tech_pulse": {
        "fn": tech_pulse,
        "description": "Fetch current Hacker News headlines, optionally filtered by a topic.",
        "parameters": {"query": "string"},
        "required": [],
    },
    "weather": {
        "fn": weather,
        "description": "Get live weather and a 3-day forecast for a city or place.",
        "parameters": {"location": "string"},
    },
    "lookup_place": {
        "fn": lookup_place,
        "description": "Geocode a place name to address, latitude, and longitude.",
        "parameters": {"query": "string"},
    },
    "qr_code": {
        "fn": qr_code,
        "description": "Generate a QR code image for a URL, text, Wi-Fi string, or contact data.",
        "parameters": {"data": "string"},
    },
    "draw_diagram": {
        "fn": draw_diagram,
        "description": (
            "Render a Mermaid flowchart, sequence, or mind-map as an image. "
            "Pass Mermaid source in 'source'."
        ),
        "parameters": {"source": "string", "kind": "string"},
        "required": ["source"],
    },
    "brand_kit": {
        "fn": brand_kit,
        "description": "Invent a brand palette, voice, logo concept, and poster for a product name.",
        "parameters": {"name": "string", "vibe": "string"},
        "required": ["name"],
    },
    "create_event": {
        "fn": create_event,
        "description": "Build a calendar .ics event from a title and ISO start time.",
        "parameters": {
            "title": "string",
            "start": "string",
            "end": "string",
            "location": "string",
            "details": "string",
        },
        "required": ["title", "start"],
    },
    "decision_canvas": {
        "fn": decision_canvas,
        "description": (
            "Build a scored decision matrix. Pass a question, comma-separated options, "
            "and optional criteria, then fill the scores in your reply."
        ),
        "parameters": {"question": "string", "options": "string", "criteria": "string"},
        "required": ["question", "options"],
    },
    "draft_email": {
        "fn": draft_email,
        "description": (
            "Create a structured email draft with recipient, subject, and body. "
            "Use this whenever the user wants to write, edit, or send an email. "
            "Never claim the email was sent after this tool — it only drafts."
        ),
        "parameters": {"to": "string", "subject": "string", "body": "string"},
    },
    "send_email": {
        "fn": send_email,
        "description": (
            "Request review of a drafted email. Suvyon displays an editable approval "
            "card and only the authenticated approval endpoint can deliver it."
        ),
        "parameters": {"to": "string", "subject": "string", "body": "string"},
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
        params = tool["parameters"] or {}
        required = tool.get("required")
        if required is None:
            required = list(params.keys())
        schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {k: {"type": v} for k, v in params.items()},
                    "required": required,
                },
            },
        })
    return schemas
