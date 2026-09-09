from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models.user import User
from app.models.workspace import Workspace
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationBranch, ConversationMerge
from app.services.chat_service import ChatService
from app.services import conversation_universes as universes


@pytest.fixture
def context():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    @event.listens_for(engine, "connect")
    def enable_fk(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
    for model in [User, Workspace, Conversation, Message]:
        model.__table__.create(engine)
    with Session(engine) as session:
        user = User(full_name="Tester", email="test@example.com", hashed_password="unused", is_verified=True)
        session.add(user)
        session.flush()
        workspace = Workspace(name="Universe", owner_id=user.id)
        session.add(workspace)
        session.flush()
        source = Conversation(workspace_id=workspace.id, title="Original", provider="test", model="small", system_prompt="Be clear.")
        session.add(source)
        session.flush()
        for role, content in [(MessageRole.USER, "Build a garden"), (MessageRole.ASSISTANT, "Try native plants"), (MessageRole.USER, "What about cost?")]:
            session.add(Message(conversation_id=source.id, role=role, content=content))
            session.flush()
        session.commit()
        chat = ChatService(ConversationRepository(session), MessageRepository(session), session)
        yield SimpleNamespace(session=session, user=user, workspace=workspace, source=source, chat=chat)
    engine.dispose()


def count_conversations(ctx):
    return ctx.session.scalar(select(func.count()).select_from(Conversation))


def test_branch_copies_prefix_with_new_ids_and_independent_content(context):
    ctx = context
    original = ctx.chat.get_messages(conversation_id=ctx.source.id)
    branch = universes.branch_conversation(ctx.chat, ctx.source, ConversationBranch(title="Bold", through_message_id=original[1].id))
    copied = ctx.chat.get_messages(conversation_id=branch.id)
    assert [m.content for m in copied] == [m.content for m in original[:2]]
    assert not {m.id for m in copied} & {m.id for m in original}
    assert branch.parent_conversation_id == ctx.source.id
    assert (branch.provider, branch.model, branch.system_prompt) == ("test", "small", "Be clear.")
    copied[0].content = "Changed branch"
    ctx.session.commit()
    assert original[0].content == "Build a garden"


def test_invalid_branch_point_creates_nothing(context):
    with pytest.raises(ValueError, match="Branch point"):
        universes.branch_conversation(context.chat, context.source, ConversationBranch(title="No", through_message_id=uuid4()))
    assert count_conversations(context) == 1


def test_branch_survives_source_deletion(context):
    branch = universes.branch_conversation(context.chat, context.source, ConversationBranch(title="Independent"))
    context.chat.delete_conversation(conversation=context.source)
    context.session.refresh(branch)
    assert branch.parent_conversation_id is None
    assert len(context.chat.get_messages(conversation_id=branch.id)) == 3


def test_branch_rolls_back_partial_copy(context, monkeypatch):
    monkeypatch.setattr(context.chat._messages, "create", lambda _: (_ for _ in ()).throw(RuntimeError("DB failed")))
    with pytest.raises(RuntimeError):
        universes.branch_conversation(context.chat, context.source, ConversationBranch(title="Failure"))
    assert count_conversations(context) == 1


def test_merge_preserves_sources_and_model_selection(context, monkeypatch):
    branch = universes.branch_conversation(context.chat, context.source, ConversationBranch(title="Alternative"))
    calls = []
    def generate(messages, **kwargs):
        calls.append((messages, kwargs))
        return SimpleNamespace(content="Use native plants in phases.", provider="test", model="small", prompt_tokens=10, completion_tokens=5)
    monkeypatch.setattr(universes, "route_chat", generate)
    merged = universes.merge_conversations(context.chat, context.workspace.id, ConversationMerge(
        conversation_ids=[context.source.id, branch.id], focus="Minimize cost", provider="test", model="small"))
    history = context.chat.get_messages(conversation_id=merged.id)
    assert len(history) == 2
    assert "Minimize cost" in history[0].content
    assert str(branch.id) in history[0].content
    assert history[1].content == "Use native plants in phases."
    assert history[1].completion_tokens == 5
    assert calls[0][1] == {"provider_name": "test", "model_id": "small"}
    assert len(context.chat.get_messages(conversation_id=context.source.id)) == 3


def test_merge_rejects_other_workspace_before_llm(context, monkeypatch):
    other = Workspace(name="Private", owner_id=context.user.id)
    context.session.add(other)
    context.session.flush()
    secret = Conversation(workspace_id=other.id, title="Secret")
    context.session.add(secret)
    context.session.commit()
    monkeypatch.setattr(universes, "route_chat", lambda *a, **kw: pytest.fail("Must not call LLM"))
    with pytest.raises(LookupError):
        universes.merge_conversations(context.chat, context.workspace.id, ConversationMerge(conversation_ids=[context.source.id, secret.id]))


@pytest.mark.parametrize("failure", ["provider", "empty", "too_long", "duplicate"])
def test_failed_merge_creates_nothing(context, monkeypatch, failure):
    branch = universes.branch_conversation(context.chat, context.source, ConversationBranch(title="Alternative"))
    def generate(*args, **kwargs):
        if failure == "provider":
            raise RuntimeError("Provider unavailable")
        if failure == "empty":
            return SimpleNamespace(content=" ")
        pytest.fail("Invalid input reached the LLM")
    monkeypatch.setattr(universes, "route_chat", generate)
    if failure == "too_long":
        context.chat.get_messages(conversation_id=branch.id)[0].content = "x" * 60001
        context.session.commit()
    ids = [context.source.id, context.source.id if failure == "duplicate" else branch.id]
    with pytest.raises((ValueError, RuntimeError)):
        universes.merge_conversations(context.chat, context.workspace.id, ConversationMerge(conversation_ids=ids))
    assert count_conversations(context) == 2


def test_routes_require_workspace_ownership(context):
    from app.api.v1.routes.conversations import router
    from app.api.dependencies import get_chat_service, get_workspace_service
    from app.api.security import get_current_verified_user
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_verified_user] = lambda: context.user
    app.dependency_overrides[get_chat_service] = lambda: context.chat
    app.dependency_overrides[get_workspace_service] = lambda: SimpleNamespace(get_workspace=lambda **kwargs: None)
    with TestClient(app) as client:
        base = f"/workspaces/{context.workspace.id}/conversations"
        assert client.post(f"{base}/{context.source.id}/branch", json={"title": "Denied"}).status_code == 404
        assert client.post(f"{base}/merge", json={"conversation_ids": [str(context.source.id), str(uuid4())]}).status_code == 404
    assert count_conversations(context) == 1


def test_authorized_routes_create_branch_and_merge(context, monkeypatch):
    from app.api.v1.routes.conversations import router
    from app.api.dependencies import get_chat_service, get_workspace_service
    from app.api.security import get_current_verified_user
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_verified_user] = lambda: context.user
    app.dependency_overrides[get_chat_service] = lambda: context.chat
    app.dependency_overrides[get_workspace_service] = lambda: SimpleNamespace(get_workspace=lambda **kwargs: context.workspace)
    monkeypatch.setattr(universes, "route_chat", lambda *a, **kw: SimpleNamespace(
        content="Synthesis", provider="test", model="small", prompt_tokens=3, completion_tokens=1))
    with TestClient(app) as client:
        base = f"/workspaces/{context.workspace.id}/conversations"
        branch = client.post(f"{base}/{context.source.id}/branch", json={"title": "Alternate"})
        assert branch.status_code == 201
        assert branch.json()["parent_conversation_id"] == str(context.source.id)
        merged = client.post(f"{base}/merge", json={"conversation_ids": [str(context.source.id), branch.json()["id"]]})
        assert merged.status_code == 201
        response = client.get(f"{base}/{merged.json()['id']}/messages")
        assert response.json()[1]["content"] == "Synthesis"
