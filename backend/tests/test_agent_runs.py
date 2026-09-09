from datetime import timedelta
from types import SimpleNamespace
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from app.models.user import User
from app.models.workspace import Workspace
from app.models.agent import Agent
from app.models.agent_message import AgentMessage
from app.models.agent_run import AgentRun
from app.schemas.agent import AgentRunRequest
from app.services import agent_runs


@pytest.fixture
def db(monkeypatch):
    engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
    for model in [User, Workspace, Agent, AgentMessage, AgentRun]:
        model.__table__.create(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(agent_runs, '_resolve', lambda *a, **kw: (None, 'selected'))
    with factory() as session:
        user = User(full_name='Test', email='test@example.com', hashed_password='unused')
        session.add(user)
        session.flush()
        workspace = Workspace(owner_id=user.id, name='Workspace')
        session.add(workspace)
        session.flush()
        agent = Agent(workspace_id=workspace.id, name='Research', instructions='Do the work', tools='calculator', provider='test', model='selected')
        session.add(agent)
        session.commit()
        yield SimpleNamespace(session=session, factory=factory, agent=agent, user=user, workspace=workspace)
    engine.dispose()


def test_persists_steps_and_server_history_with_requested_model(db, monkeypatch):
    db.session.add(AgentMessage(agent_id=db.agent.id, role='user', content='Earlier context'))
    db.session.commit()
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='Calculate', provider='other', model='exact'))
    def execute(agent, content, history, emit, **kwargs):
        assert agent.provider == 'other' and agent.model == 'exact'
        assert history == [dict(role='user', content='Earlier context')]
        emit(dict(kind='tool_finished', summary='Calculated', output='2'))
        emit(dict(kind='model_finished', summary='Answer', provider='other', model='reported-version'))
        return dict(status='completed', content='The answer is 2.', pending_email=None)
    monkeypatch.setattr(agent_runs, 'execute_agent', execute)
    agent_runs.perform_run(run.id, db.factory)
    db.session.refresh(run)
    assert run.status == 'completed'
    assert len(run.events) == 2
    assert run.model == 'reported-version'
    saved = db.session.scalars(select(AgentMessage).where(AgentMessage.agent_id == db.agent.id)).all()
    assert len(saved) == 3
    assert any('Model: other/reported-version' in m.content for m in saved)


def test_only_one_active_run_and_no_duplicate_user_message(db):
    agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='One'))
    with pytest.raises(IntegrityError):
        agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='Two'))
    db.session.rollback()
    assert len(db.session.scalars(select(AgentMessage)).all()) == 1


def test_expired_run_is_interrupted_and_releases_slot(db):
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='One'))
    run.expires_at = agent_runs.now() - timedelta(seconds=1)
    db.session.commit()
    agent_runs.expire_runs(db.session, db.agent.id)
    db.session.refresh(run)
    assert run.status == 'interrupted'
    second = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='Two'))
    assert second.status == 'queued'


def test_stop_during_execution_does_not_become_completed(db, monkeypatch):
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='One'))
    def execute(*a, emit, should_stop, **kw):
        with db.factory() as other:
            current = other.get(AgentRun, run.id)
            current.status = 'stopping'
            other.commit()
        emit(dict(kind='tool_finished', summary='In-flight result', output='Kept'))
        assert should_stop()
        return dict(status='completed', content='Must not win', pending_email=None)
    monkeypatch.setattr(agent_runs, 'execute_agent', execute)
    agent_runs.perform_run(run.id, db.factory)
    db.session.refresh(run)
    assert run.status == 'cancelled'
    assert run.events[0]['output'] == 'Kept'


def test_unexpected_failure_keeps_prior_steps(db, monkeypatch):
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='One'))
    def execute(*a, emit, **kw):
        emit(dict(kind='tool_finished', summary='Completed step', output='Kept'))
        raise RuntimeError('Crash')
    monkeypatch.setattr(agent_runs, 'execute_agent', execute)
    agent_runs.perform_run(run.id, db.factory)
    db.session.refresh(run)
    assert run.status == 'failed'
    assert run.events[0]['output'] == 'Kept'


def test_run_routes_enforce_ownership(db):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.v1.routes.agents import router
    from app.api.dependencies import get_workspace_service, get_agent_service
    from app.api.security import get_current_verified_user
    from app.core.database import get_db
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db.session
    app.dependency_overrides[get_current_verified_user] = lambda: db.user
    app.dependency_overrides[get_workspace_service] = lambda: SimpleNamespace(get_workspace=lambda **kw: None)
    app.dependency_overrides[get_agent_service] = lambda: None
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='One'))
    with TestClient(app) as client:
        base = f'/workspaces/{db.workspace.id}/agents/{db.agent.id}/runs'
        assert client.get(base).status_code == 404
        assert client.post(base, json={'content':'No access'}).status_code == 404
        assert client.post(f'{base}/{run.id}/stop').status_code == 404
    db.session.refresh(run)
    assert run.status == 'queued'


def test_saved_email_approval_cannot_send_twice(db, monkeypatch):
    from fastapi import HTTPException
    from app.api.v1.routes import agents as routes
    from app.schemas.agent import AgentEmailSendRequest
    from app.services.agent_service import AgentService
    from app.repositories.agent_repository import AgentRepository
    from app.repositories.agent_message_repository import AgentMessageRepository
    db.agent.tools = 'draft_email,send_email'
    db.session.commit()
    run = agent_runs.create_run(db.session, db.agent, AgentRunRequest(content='Draft'))
    run.status = 'awaiting_approval'
    run.pending_email = dict(to='a@example.com', subject='Hi', body='Hello', regards='')
    db.session.commit()
    calls = []
    monkeypatch.setattr(routes, 'send_approved_email', lambda **kw: calls.append(kw) or 'Delivered')
    request = AgentEmailSendRequest(**run.pending_email, confirmed=True, run_id=run.id)
    kwargs = dict(workspace_id=db.workspace.id, agent_id=db.agent.id, request=request,
        current_user=db.user, workspace_service=SimpleNamespace(get_workspace=lambda **kw: db.workspace),
        agent_service=AgentService(AgentRepository(db.session), AgentMessageRepository(db.session)), session=db.session)
    routes.send_agent_email(**kwargs)
    assert run.pending_email is None
    assert run.status == 'completed'
    with pytest.raises(HTTPException) as exc:
        routes.send_agent_email(**kwargs)
    assert exc.value.status_code == 409
    assert len(calls) == 1
