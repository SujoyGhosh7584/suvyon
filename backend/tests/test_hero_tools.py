"""Free studio/research tools should not require paid APIs."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.media import generate_image, generate_speech, generate_storyboard, image_url
from app.tools.studio import brand_kit, create_event, decision_canvas, draw_diagram, qr_code
from app.tools.registry import list_tools


def test_registry_includes_hero_tools():
    names = set(list_tools())
    for name in (
        "generate_image",
        "generate_storyboard",
        "generate_speech",
        "wikipedia",
        "arxiv_search",
        "read_page",
        "tech_pulse",
        "weather",
        "lookup_place",
        "qr_code",
        "draw_diagram",
        "brand_kit",
        "create_event",
        "decision_canvas",
    ):
        assert name in names


def test_generate_image_returns_markdown_url():
    result = generate_image("a red bicycle in rain", aspect="wide")
    assert "image.pollinations.ai" in result
    assert "gen.pollinations.ai" not in result
    assert "enhance=" not in result
    assert "![" in result
    assert image_url("a red bicycle in rain").startswith("https://image.pollinations.ai/")


def test_generate_storyboard_is_playable_sequence():
    result = generate_storyboard("night market in tokyo", frames="4")
    assert "[[suvyon:storyboard]]" in result
    raw = result.split("[[suvyon:storyboard]]")[1].split("[[/suvyon:storyboard]]")[0]
    payload = json.loads(raw)
    assert len(payload["frames"]) == 4
    assert all(frame["url"].startswith("https://") for frame in payload["frames"])


def test_generate_speech_keeps_marker():
    result = generate_speech("The rain in Spain.")
    assert "[[suvyon:speak]]The rain in Spain.[[/suvyon:speak]]" in result


def test_brand_kit_and_qr_and_diagram():
    kit = brand_kit("Northline", "quiet, technical")
    assert "#" in kit
    assert "![logo]" in kit
    qr = qr_code("https://suvyon.app")
    assert "api.qrserver.com" in qr
    diagram = draw_diagram("graph TD; A-->B;")
    assert "kroki.io" in diagram
    assert "![diagram]" in diagram


def test_event_and_decision_canvas():
    ics = create_event("Demo", "2026-09-01T15:00:00", location="Studio")
    assert "BEGIN:VEVENT" in ics
    canvas = decision_canvas("Which model?", "Groq, Gemini, local")
    assert "Groq" in canvas and "Gemini" in canvas
