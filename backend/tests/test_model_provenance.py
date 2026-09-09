import httpx
import pytest
from app.ai.providers import groq, openrouter, gemini
from app.ai.providers.base import LLMMessage


@pytest.mark.parametrize(('module', 'class_name'), [(groq, 'GroqProvider'), (openrouter, 'OpenRouterProvider')])
def test_provider_uses_reported_model(module, class_name, monkeypatch):
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, *args, **kwargs):
            return httpx.Response(200, request=httpx.Request('POST', 'https://example.com'),
                json={'model':'actual/model-version', 'choices':[{'message':{'content':'Hello'}}], 'usage':{}})
    monkeypatch.setattr(module.httpx, 'Client', Client)
    result = getattr(module, class_name)().chat([LLMMessage(role='user', content='hello')], 'router-alias')
    assert result.model == 'actual/model-version'


def test_gemini_uses_reported_version(monkeypatch):
    monkeypatch.setattr(gemini.GeminiProvider, '_post_generate', lambda *args: {
        'modelVersion':'gemini-reported-version', 'candidates':[{'content':{'parts':[{'text':'Hello'}]}}]})
    result = gemini.GeminiProvider().chat([LLMMessage(role='user', content='hello')], 'gemini-flash-latest')
    assert result.model == 'gemini-reported-version'


def test_stream_reports_metadata_without_sending_it_in_payload(monkeypatch):
    from app.ai import router
    from app.ai.providers.base import ModelInfo
    class Provider:
        provider_name = 'test'
        def is_available(self): return True
        def list_models(self): return [ModelInfo('test', 'alias', 'Alias', 1000)]
        def stream(self, messages, model, **kwargs):
            kwargs['_metadata']['model'] = 'actual-version'
            yield 'hello'
    provider = Provider()
    monkeypatch.setattr(router, 'get_available_providers', lambda: [provider])
    monkeypatch.setattr(router, 'get_provider', lambda name: provider)
    metadata = {}
    assert list(router.route_stream([], 'test', 'alias', metadata=metadata)) == ['hello']
    assert metadata == {'provider':'test', 'model':'actual-version'}
