import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.providers.base import LLMResponse
from app.services.chat_service import ChatService


def test_auto_uses_tools_when_model_requests_wikipedia(monkeypatch):
    calls = {"n": 0}

    def fake_route_chat(messages, provider_name=None, model_id=None, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            assert kwargs.get("tools")
            return LLMResponse(
                content="",
                provider="groq",
                model="test",
                tool_calls=[
                    {
                        "id": "1",
                        "name": "wikipedia",
                        "arguments": {"query": "Chief Minister of West Bengal"},
                    }
                ],
            )
        return LLMResponse(
            content="Mamata Banerjee per Wikipedia.",
            provider="groq",
            model="test",
        )

    monkeypatch.setattr("app.services.chat_service.route_chat", fake_route_chat)
    monkeypatch.setattr(
        "app.services.chat_service._call_tool",
        lambda name, arguments, **kwargs: "Title: CM\nURL: https://en.wikipedia.org/wiki/x\nMamata Banerjee",
    )

    service = ChatService.__new__(ChatService)
    service._session = None
    service._messages = SimpleNamespace(get_by_conversation=lambda conversation_id: [])
    conversation = SimpleNamespace(
        id="c1",
        workspace_id="ws-1",
        system_prompt=None,
        provider="groq",
        model="test",
    )
    monkeypatch.setattr(service, "_get_active_knowledge_bases", lambda workspace_id: [])

    text, mode, sources, provider, model = service._answer_with_tools(
        conversation=conversation,
        content="what is the name of the CM of West Bengal?",
    )
    assert mode == "web"
    assert "Mamata" in text
    assert provider == "groq"


def test_auto_image_tool_is_chat_not_web(monkeypatch):
    calls = {"n": 0}

    def fake_route_chat(messages, provider_name=None, model_id=None, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return LLMResponse(
                content="",
                provider="groq",
                model="test",
                tool_calls=[
                    {
                        "id": "1",
                        "name": "generate_image",
                        "arguments": {"prompt": "a cow grazing"},
                    }
                ],
            )
        return LLMResponse(
            content="![cow](https://image.pollinations.ai/prompt/cow)",
            provider="groq",
            model="test",
        )

    monkeypatch.setattr("app.services.chat_service.route_chat", fake_route_chat)
    monkeypatch.setattr(
        "app.services.chat_service._call_tool",
        lambda name, arguments, **kwargs: "![cow](https://image.pollinations.ai/prompt/cow)",
    )

    service = ChatService.__new__(ChatService)
    service._session = None
    service._messages = SimpleNamespace(get_by_conversation=lambda conversation_id: [])
    conversation = SimpleNamespace(
        id="c1",
        workspace_id="ws-1",
        system_prompt=None,
        provider="groq",
        model="test",
    )
    monkeypatch.setattr(service, "_get_active_knowledge_bases", lambda workspace_id: [])

    text, mode, sources, *_ = service._answer_with_tools(
        conversation=conversation,
        content="Generate a cow image",
    )
    assert mode == "chat"
    assert sources == []
    assert "cow" in text.lower()


def test_auto_skips_tools_for_plain_answer(monkeypatch):
    monkeypatch.setattr(
        "app.services.chat_service.route_chat",
        lambda *args, **kwargs: LLMResponse(
            content="def snake():\n    pass",
            provider="groq",
            model="test",
        ),
    )
    service = ChatService.__new__(ChatService)
    service._session = None
    service._messages = SimpleNamespace(get_by_conversation=lambda conversation_id: [])
    conversation = SimpleNamespace(
        id="c1",
        workspace_id="ws-1",
        system_prompt=None,
        provider="groq",
        model="test",
    )
    monkeypatch.setattr(service, "_get_active_knowledge_bases", lambda workspace_id: [])

    text, mode, sources, *_ = service._answer_with_tools(
        conversation=conversation,
        content="write a snake game in python",
    )
    assert mode == "chat"
    assert "snake" in text.lower()
    assert sources == []


def test_provenance_note_lists_rag_sources():
    service = ChatService.__new__(ChatService)
    note = service._build_provenance_note(
        "rag", "openrouter", "gpt-4o-mini", ["HR KB: resume.pdf"]
    )
    assert "knowledge base" in note.lower()
    assert "resume.pdf" in note


def test_build_contextual_messages_web_mode(monkeypatch):
    service = ChatService.__new__(ChatService)
    service._messages = SimpleNamespace(get_by_conversation=lambda conversation_id: [])
    conversation = SimpleNamespace(id="conv-1", workspace_id="ws-1", system_prompt=None)
    monkeypatch.setattr(
        "app.services.chat_service.web_search",
        lambda *_args, **_kwargs: "search result",
    )
    monkeypatch.setattr("app.services.chat_service.wikipedia", lambda *_args, **_kwargs: "")

    messages, sources = service._build_contextual_messages(
        conversation=conversation,
        content="What is the latest AI news?",
        mode="web",
    )
    assert len(messages) == 2
    assert messages[1].role == "user"
    assert "search result" in messages[1].content
    assert sources == []
