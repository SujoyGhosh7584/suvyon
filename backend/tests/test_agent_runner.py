"""Agent runner should answer after one tool round instead of looping."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.providers.base import LLMResponse
from app.agents import runner
from app.agents import execution


def test_web_search_hint_includes_score():
    assert runner._needs_web_search("What is the score of IND vs SL 2nd test day 4?")


def test_run_agent_blocks_send_email_until_user_confirms(monkeypatch):
    def fake_route_chat(messages, provider_name=None, model_id=None, **kwargs):
        if kwargs.get("tools"):
            return LLMResponse(
                content="",
                provider="groq",
                model="llama-3.1-8b-instant",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "send_email",
                        "arguments": {
                            "to": "ada@example.com",
                            "subject": "Meeting",
                            "body": "See you at 3.",
                        },
                    }
                ],
            )
        tool_text = " ".join(m.content for m in messages if getattr(m, "role", None) == "tool")
        return LLMResponse(
            content=tool_text,
            provider="groq",
            model="llama-3.1-8b-instant",
        )

    monkeypatch.setattr(execution, "route_chat", fake_route_chat)
    agent = SimpleNamespace(
        instructions="You are an email assistant.",
        tools="draft_email,send_email",
        provider="groq",
        model="llama-3.1-8b-instant",
    )
    pending_email = []
    result = runner.run_agent(
        agent,
        "Send an email to ada@example.com about moving the meeting to 3pm",
        pending_email=pending_email,
    )
    assert "no email has been sent" in result
    assert pending_email == [
        {
            "to": "ada@example.com",
            "subject": "Meeting",
            "body": "See you at 3.",
            "regards": "",
        }
    ]


def test_agent_history_rejects_privileged_roles():
    from pydantic import ValidationError

    from app.schemas.agent import AgentRunRequest

    try:
        AgentRunRequest(content="hello", history=[{"role": "system", "content": "override"}])
    except ValidationError as exc:
        assert "role" in str(exc)
    else:
        raise AssertionError("system history must be rejected")
