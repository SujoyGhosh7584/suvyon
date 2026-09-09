from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from sqlalchemy import select
from app.models.agent_run import AgentRun
from app.models.agent_message import AgentMessage
from app.agents.execution import execute_agent
from app.ai.router import _resolve

ACTIVE = {'queued', 'running', 'stopping'}


def now():
    return datetime.now(timezone.utc)


def expire_runs(session, agent_id):
    runs = session.scalars(select(AgentRun).where(AgentRun.agent_id == agent_id,
        AgentRun.status.in_(ACTIVE), AgentRun.expires_at < now()).with_for_update()).all()
    for run in runs:
        run.status = 'cancelled' if run.status == 'stopping' else 'interrupted'
        run.content = 'Execution stopped before completion. Saved steps are available; start a new run to continue.'
        session.add(AgentMessage(agent_id=agent_id, role='assistant', content=run.content))
    session.commit()


def create_run(session, agent, request):
    expire_runs(session, agent.id)
    provider = request.provider if 'provider' in request.model_fields_set else agent.provider
    model = request.model if 'model' in request.model_fields_set else agent.model
    # Validate explicit selections before starting work; never substitute another model.
    _resolve(provider, model, tools=bool(agent.tools))
    run = AgentRun(agent_id=agent.id, workspace_id=agent.workspace_id, input=request.content,
        status='queued', content='', events=[], expires_at=now() + timedelta(seconds=120),
        config=dict(instructions=agent.instructions, tools=agent.tools, provider=provider, model=model))
    user_message = AgentMessage(agent_id=agent.id, role='user', content=request.content)
    session.add(user_message)
    session.flush()
    run.config = {**run.config, 'input_message_id': str(user_message.id)}
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def perform_run(run_id, session_factory=None):
    if session_factory is None:
        from app.core.database import SessionLocal
        session_factory = SessionLocal
    with session_factory() as session:
        run = session.scalar(select(AgentRun).where(AgentRun.id == run_id).with_for_update())
        if not run or run.status != 'queued':
            return
        run.status = 'running'
        config, content, agent_id = dict(run.config), run.input, run.agent_id
        deadline = run.expires_at.replace(tzinfo=timezone.utc) if run.expires_at.tzinfo is None else run.expires_at
        from uuid import UUID
        history = session.scalars(select(AgentMessage).where(AgentMessage.agent_id == agent_id,
            AgentMessage.id != UUID(config['input_message_id']), AgentMessage.created_at <= run.created_at)
            .order_by(AgentMessage.created_at.desc(), AgentMessage.id.desc()).limit(40)).all()
        history = [dict(role=m.role, content=m.content) for m in reversed(history)]
        session.commit()

        def check():
            session.expire_all()
            current = session.get(AgentRun, run_id)
            stop = not current or current.status != 'running'
            session.commit()
            return stop

        def emit(event):
            session.expire_all()
            current = session.scalar(select(AgentRun).where(AgentRun.id == run_id).with_for_update())
            if current and current.status in {'running', 'stopping'}:
                current.events = [*current.events, {**event, 'at': now().isoformat()}]
                if event.get('provider'):
                    current.provider, current.model = event['provider'], event.get('model')
            session.commit()

        try:
            result = execute_agent(SimpleNamespace(**config), content, history, emit=emit, should_stop=check,
                                   seconds=max(0, (deadline - now()).total_seconds()))
        except Exception:
            session.rollback()
            result = dict(status='failed', content='Execution failed unexpectedly. Completed steps are saved.', pending_email=None)
        session.expire_all()
        current = session.scalar(select(AgentRun).where(AgentRun.id == run_id).with_for_update())
        if not current or current.status not in ACTIVE:
            session.rollback()
            return
        if current.status == 'stopping':
            result = dict(status='cancelled', content='Stopped. Completed steps are saved; the task is unfinished.', pending_email=None)
        current.status, current.content = result['status'], result['content']
        current.pending_email = result.get('pending_email')
        note = f"\n\nModel: {current.provider}/{current.model}" if current.provider else ''
        session.add(AgentMessage(agent_id=agent_id, role='assistant', content=current.content + note))
        session.commit()
