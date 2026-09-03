from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.routes import agents as agent_routes
from app.schemas.agent import AgentRunRequest


class FakeAgentService:
    def __init__(self):
        self.agent = SimpleNamespace(
            id=uuid4(),
            is_active=True,
            instructions="Help the user.",
            tools="",
            provider=None,
            model=None,
        )
        self.persisted_history = [
            SimpleNamespace(role="user", content="server-side question"),
            SimpleNamespace(role="assistant", content="server-side answer"),
        ]
        self.saved_exchange = None

    def get_agent(self, *, agent_id, workspace_id):
        return self.agent

    def get_recent_history(self, *, agent_id):
        assert agent_id == self.agent.id
        return self.persisted_history

    def append_exchange(self, **exchange):
        self.saved_exchange = exchange


def test_agent_run_uses_and_persists_server_history(monkeypatch):
    service = FakeAgentService()
    captured = {}

    def fake_run_agent(agent, content, history, pending_email):
        captured["history"] = history
        return "new server-side answer"

    monkeypatch.setattr(agent_routes, "run_agent", fake_run_agent)
    workspace_id = uuid4()
    response = agent_routes.run(
        workspace_id=workspace_id,
        agent_id=service.agent.id,
        request=AgentRunRequest(
            content="new question",
            history=[{"role": "user", "content": "untrusted browser history"}],
        ),
        current_user=SimpleNamespace(id=uuid4()),
        workspace_service=SimpleNamespace(
            get_workspace=lambda **kwargs: SimpleNamespace(id=workspace_id)
        ),
        agent_service=service,
    )

    assert captured["history"] == service.persisted_history
    assert service.saved_exchange == {
        "agent_id": service.agent.id,
        "user_content": "new question",
        "assistant_content": "new server-side answer",
    }
    assert response.content == "new server-side answer"
