import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.chat_service import ChatService


def test_intent_router_classifies_web_search_and_rag():
    service = ChatService.__new__(ChatService)

    assert service._classify_request("What is the latest AI trend?") == "web"
    assert service._classify_request("What is the gold rate today?") == "web"
    assert service._classify_request("Summarize the uploaded contract") == "rag"
    assert service._classify_request("Whose resume is it?") == "rag"
    assert service._classify_request("Explain machine learning basics") == "chat"
    assert service._classify_request("What is the capital of France?") == "chat"
    # Live/web keywords should win over generic RAG phrases
    assert service._classify_request("tell me about the gold rate today") == "web"
    assert service._classify_request("current gold rate") == "web"


def test_provenance_note_lists_rag_sources():
    service = ChatService.__new__(ChatService)
    note = service._build_provenance_note(
        "rag", "openrouter", "gpt-4o-mini", ["HR KB: resume.pdf"]
    )

    assert "knowledge base" in note.lower()
    assert "resume.pdf" in note


def test_build_contextual_messages_appends_first_user_turn_without_history(monkeypatch):
    service = ChatService.__new__(ChatService)
    service._messages = SimpleNamespace(get_by_conversation=lambda conversation_id: [])
    conversation = SimpleNamespace(id="conv-1", workspace_id="ws-1", system_prompt=None)

    monkeypatch.setattr(
        "app.services.chat_service.web_search",
        lambda *_args, **_kwargs: "search result",
    )

    messages, sources = service._build_contextual_messages(
        conversation=conversation,
        content="What is the latest AI news?",
        mode="web",
    )

    assert len(messages) == 1
    assert messages[0].role == "user"
    assert "search result" in messages[0].content
    assert sources == []
