from __future__ import annotations

import hashlib
import json
from urllib.parse import quote

_IMAGE_BASE = "https://image.pollinations.ai/prompt"
_ASPECTS = {
    "square": (1024, 1024),
    "wide": (1280, 720),
    "portrait": (768, 1280),
    "photo": (1024, 1024),
}

_STORY_SHOTS = (
    ("Wide establishing shot", "cinematic wide establishing shot, environment, lighting"),
    ("Medium shot", "medium shot, subject clearly visible, film still"),
    ("Close-up", "dramatic close-up, emotion, shallow depth of field"),
    ("Action / payoff", "dynamic finale shot, motion, cinematic composition"),
    ("Detail insert", "macro detail insert shot, texture, storytelling prop"),
    ("Closing frame", "quiet closing frame, aftermath, cinematic still"),
)


def image_url(prompt: str, *, aspect: str = "square", seed: int | None = None) -> str:
    cleaned = " ".join((prompt or "").split())
    if not cleaned:
        cleaned = "abstract luminous shape, high quality"
    width, height = _ASPECTS.get((aspect or "square").lower(), _ASPECTS["square"])
    if seed is None:
        seed = int(hashlib.sha256(cleaned.encode()).hexdigest()[:8], 16)
    encoded = quote(cleaned)
    return (
        f"{_IMAGE_BASE}/{encoded}"
        f"?width={width}&height={height}&nologo=true&enhance=true&seed={seed}"
    )


def generate_image(prompt: str, aspect: str = "square") -> str:
    """Create a free AI image URL (Pollinations, no API key)."""
    if not (prompt or "").strip():
        return "Tool error: generate_image requires a prompt."
    url = image_url(prompt, aspect=aspect)
    return (
        f"Generated image for: {prompt.strip()}\n\n"
        f"![{prompt.strip()}]({url})\n\n"
        f"Open full size: {url}\n"
        "This uses a free public image model. Include the markdown image in your reply."
    )


def generate_storyboard(prompt: str, frames: str = "4") -> str:
    """Free 'video' alternative: a directed multi-shot visual sequence."""
    if not (prompt or "").strip():
        return "Tool error: generate_storyboard requires a prompt describing the scene."
    try:
        count = max(3, min(6, int(str(frames).strip() or "4")))
    except (TypeError, ValueError):
        count = 4

    items = []
    for index, (shot, extra) in enumerate(_STORY_SHOTS[:count], start=1):
        frame_prompt = f"{prompt.strip()}, {extra}, storyboard frame {index}"
        url = image_url(frame_prompt, aspect="wide", seed=10_000 + index * 97)
        items.append({"shot": shot, "caption": frame_prompt, "url": url})

    payload = {"title": prompt.strip(), "frames": items}
    lines = [
        f"Storyboard for: {prompt.strip()}",
        "True text-to-video APIs are paid; this is a free cinematic shot sequence the UI can play as a clip.",
        "",
        f"[[suvyon:storyboard]]{json.dumps(payload)}[[/suvyon:storyboard]]",
        "",
    ]
    for item in items:
        lines.append(f"- **{item['shot']}**: {item['url']}")
    return "\n".join(lines)


def generate_speech(text: str) -> str:
    """Mark narration for the free in-browser voiceover player."""
    script = " ".join((text or "").split())
    if not script:
        return "Tool error: generate_speech requires text to speak."
    return (
        "Voiceover is ready. The app will play this with the device speech engine (no paid TTS API).\n\n"
        f"[[suvyon:speak]]{script}[[/suvyon:speak]]"
    )
