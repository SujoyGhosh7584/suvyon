from types import SimpleNamespace
from uuid import uuid4

from app.ai.providers.base import LLMResponse
from app.services.chat_service import ChatService


def _service():
    service = ChatService.__new__(ChatService)
    service._session = object()
    service._messages = SimpleNamespace(get_by_conversation=lambda _id: [])
    return service


def test_selected_knowledge_base_keeps_chat_files_and_excludes_other_bases(monkeypatch):
    service = _service()
    workspace_id = uuid4()
    conversation_id = uuid4()
    selected_id = uuid4()
    other_id = uuid4()
    chat_id = uuid4()
    bases = [
        SimpleNamespace(id=selected_id, name="Selected", conversation_id=None),
        SimpleNamespace(id=other_id, name="Other", conversation_id=None),
        SimpleNamespace(id=chat_id, name="Chat files", conversation_id=conversation_id),
    ]
    searched = []

    monkeypatch.setattr(
        service,
        "_get_active_knowledge_bases",
        lambda workspace_id, conversation_id=None: bases,
    )

    def fake_retrieve(_session, kb_id, _query, **_kwargs):
        searched.append(kb_id)
        return ([f"context-{kb_id}"], [f"source-{kb_id}"])

    monkeypatch.setattr(
        "app.services.chat_service.retrieve_context_with_sources",
        fake_retrieve,
    )

    service._build_rag_context(
        workspace_id,
        "question",
        knowledge_base_id=selected_id,
        conversation_id=conversation_id,
    )

    assert searched == [selected_id, chat_id]
    assert other_id not in searched


def test_auto_tool_path_forwards_selected_knowledge_bases(monkeypatch):
    service = _service()
    selected_id = uuid4()
    conversation_id = uuid4()
    captured = {}
    calls = {"count": 0}

    monkeypatch.setattr(
        service,
        "_get_active_knowledge_bases",
        lambda workspace_id, conversation_id=None: [object()],
    )

    def fake_route_chat(*_args, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return LLMResponse(
                content="",
                provider="test",
                model="test",
                tool_calls=[
                    {
                        "id": "tool-1",
                        "name": "search_knowledge",
                        "arguments": {"query": "project"},
                    }
                ],
            )
        return LLMResponse(content="answer", provider="test", model="test")

    def fake_run_tool(name, arguments, workspace_id, **kwargs):
        captured.update(kwargs)
        return "context", ["project.pdf"]

    monkeypatch.setattr("app.services.chat_service.route_chat", fake_route_chat)
    monkeypatch.setattr(service, "_run_chat_tool", fake_run_tool)

    conversation = SimpleNamespace(
        id=conversation_id,
        workspace_id=uuid4(),
        system_prompt=None,
        provider="test",
        model="test",
    )
    service._answer_with_tools(
        conversation=conversation,
        content="What does my project say?",
        knowledge_base_ids=[selected_id],
    )

    assert captured["knowledge_base_ids"] == [selected_id]
    assert captured["conversation_id"] == conversation_id


def test_empty_selection_excludes_shared_bases_but_keeps_chat_files(monkeypatch):
    service = _service()
    workspace_id = uuid4()
    conversation_id = uuid4()
    shared_id = uuid4()
    chat_id = uuid4()
    bases = [
        SimpleNamespace(id=shared_id, name="Shared", conversation_id=None),
        SimpleNamespace(id=chat_id, name="Chat files", conversation_id=conversation_id),
    ]
    searched = []
    monkeypatch.setattr(service, "_get_active_knowledge_bases", lambda *_args, **_kwargs: bases)
    monkeypatch.setattr(
        "app.services.chat_service.retrieve_context_with_sources",
        lambda _session, kb_id, _query, **_kwargs: (searched.append(kb_id) or ["context"], ["file.pdf"]),
    )

    service._build_rag_context(
        workspace_id,
        "question",
        knowledge_base_ids=[],
        conversation_id=conversation_id,
    )

    assert searched == [chat_id]
