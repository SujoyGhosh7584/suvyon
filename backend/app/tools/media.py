from __future__ import annotations

import json
import secrets
from urllib.parse import quote

_IMAGE_BASE = "https://image.pollinations.ai/prompt"
_DEFAULT_MODEL = "sana"
_PROMPT_MAX = 360
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


def _clean_prompt(prompt: str) -> str:
    cleaned = " ".join((prompt or "").split())
    if not cleaned:
        cleaned = "abstract luminous shape, high quality"
    quality = "photorealistic, anatomically correct, single coherent subject"
    if "photorealistic" not in cleaned.lower():
        cleaned = f"{cleaned}, {quality}"
    return cleaned[:_PROMPT_MAX]


def image_url(prompt: str, *, aspect: str = "square", seed: int | None = None) -> str:
    """Public Pollinations URL. Do not use gen.pollinations.ai (it requires an API key)."""
    cleaned = _clean_prompt(prompt)
    width, height = _ASPECTS.get((aspect or "square").lower(), _ASPECTS["square"])
    if seed is None:
        seed = secrets.randbelow(2_147_483_647)
    encoded = quote(cleaned, safe="")
    return (
        f"{_IMAGE_BASE}/{encoded}"
        f"?model={_DEFAULT_MODEL}&width={width}&height={height}"
        f"&nologo=true&seed={seed}"
    )


def generate_image(prompt: str, aspect: str = "square") -> str:
    """Return markdown that points at a hosted Pollinations image (nothing stored locally)."""
    if not (prompt or "").strip():
        return "Tool error: generate_image requires a prompt."
    alt = prompt.strip().replace("]", "").replace("\n", " ")[:80]
    url = image_url(prompt, aspect=aspect)
    return (
        f"Generated image for: {prompt.strip()}\n\n"
        f"![{alt}]({url})\n\n"
        f"Open full size: {url}\n"
        "Include the markdown image in your reply."
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
