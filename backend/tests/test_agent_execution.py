from types import SimpleNamespace
from app.ai.providers.base import LLMResponse
from app.agents import execution


def agent(tools='web_search,read_page,calculator'):
    return SimpleNamespace(instructions='Complete the task.', tools=tools, provider='test', model='selected')


def response(name=None, args=None, content='Done with sources and limitations.'):
    return LLMResponse(content='' if name else content, provider='test', model='reported-version', routing_model='selected',
        tool_calls=[dict(id='call', name=name, arguments=args)] if name else None)


def test_search_read_calculate_then_answer(monkeypatch):
    replies = iter([response('web_search', {'query': 'hosting costs'}),
        response('read_page', {'url': 'https://example.com/a'}),
        response('read_page', {'url': 'https://example.com/b'}),
        response('calculator', {'expression': '10*12'}), response()])
    model_calls, tool_calls, events = [], [], []
    def call(messages, **kw):
        model_calls.append((list(messages), kw))
        return next(replies)
    monkeypatch.setattr(execution, 'route_chat', call)
    monkeypatch.setattr(execution, '_call_tool', lambda name, args, **kw: tool_calls.append(name) or 'Verified tool output')
    result = execution.execute_agent(agent(), 'Compare hosting costs', emit=events.append)
    assert result['status'] == 'completed'
    assert tool_calls == ['web_search', 'read_page', 'read_page', 'calculator']
    assert len(model_calls) == 5
    assert len([m for m in model_calls[-1][0] if m.role == 'tool']) == 4
    assert all(call[1]['model_id'] == 'selected' for call in model_calls)
    assert result['model'] == 'reported-version'
    assert len([e for e in events if e['kind'] == 'tool_finished']) == 4


def test_disabled_tool_never_executes(monkeypatch):
    replies = iter([response('send_email', {'to':'a@example.com', 'subject':'Hi', 'body':'Hello'}), response()])
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: next(replies))
    monkeypatch.setattr(execution, '_call_tool', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('Disabled tool executed')))
    events = []
    execution.execute_agent(agent('calculator'), 'Do something', emit=events.append)
    assert any(e['kind'] == 'tool_failed' and 'not enabled' in e['output'] for e in events)


def test_failed_tool_retries_then_recovers(monkeypatch):
    replies = iter([response('read_page', {'url':'https://example.com'}), response('read_page', {'url':'https://example.com'}), response()])
    outputs = iter(['Tool error: timeout', 'Page text'])
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: next(replies))
    monkeypatch.setattr(execution, '_call_tool', lambda *a, **kw: next(outputs))
    events = []
    result = execution.execute_agent(agent(), 'Read this', emit=events.append)
    assert result['status'] == 'completed'
    assert len([e for e in events if e['kind'] == 'tool_failed']) == 1
    assert len([e for e in events if e['kind'] == 'tool_finished']) == 1


def test_repeated_success_does_not_repeat_tool(monkeypatch):
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: response('calculator', {'expression':'1+1'}))
    calls = []
    monkeypatch.setattr(execution, '_call_tool', lambda *a, **kw: calls.append(a) or '2')
    result = execution.execute_agent(agent(), 'Calculate', max_turns=4)
    assert result['status'] == 'limited'
    assert len(calls) == 1


def test_cancellation_after_tool_preserves_event_and_stops(monkeypatch):
    state = {'stop': False}
    events = []
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: response('calculator', {'expression':'1+1'}))
    def tool(*a, **kw):
        state['stop'] = True
        return '2'
    monkeypatch.setattr(execution, '_call_tool', tool)
    result = execution.execute_agent(agent(), 'Calculate', should_stop=lambda: state['stop'], emit=events.append)
    assert result['status'] == 'cancelled'
    assert events[-1]['kind'] == 'tool_finished'


def test_invalid_arguments_are_not_executed(monkeypatch):
    replies = iter([response('calculator', {'expression': 123}), response()])
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: next(replies))
    monkeypatch.setattr(execution, '_call_tool', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('Bad arguments executed')))
    events = []
    execution.execute_agent(agent(), 'Calculate', emit=events.append)
    assert any(e['kind'] == 'tool_failed' for e in events)


def test_time_budget_stops_before_model(monkeypatch):
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('Out of time')))
    assert execution.execute_agent(agent(), 'Calculate', seconds=0)['status'] == 'limited'


def test_model_failure_is_not_reported_as_completion(monkeypatch):
    monkeypatch.setattr(execution, 'route_chat', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('selected model down')))
    assert execution.execute_agent(agent(), 'Calculate')['status'] == 'failed'
