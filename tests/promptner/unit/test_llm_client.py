"""Unit-Tests fuer den LLM-Client (Fake-Backend, kein Key noetig)."""

from types import SimpleNamespace

import pytest

from promptner.config.settings import Settings
from promptner.errors import ErrorCode, PromptNerError
from promptner.llm.client import ChatRequest, LlmClient, list_model_ids


class _FakeCompletions:
    def __init__(self, content=None, error=None):
        self._content, self._error, self.calls = content, error, []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


class _FakeModels:
    def __init__(self, ids):
        self._ids = ids

    def list(self):
        return SimpleNamespace(data=[SimpleNamespace(id=i) for i in self._ids])


class _FakeSdk:
    def __init__(self, content=None, error=None, model_ids=()):
        self.completions = _FakeCompletions(content, error)
        self.chat = SimpleNamespace(completions=self.completions)
        self.models = _FakeModels(list(model_ids))


def _settings(**kw):
    return Settings(_env_file=None, **kw)


@pytest.mark.unit
def test_complete_returns_text_and_passes_model_and_temperature():
    sdk = _FakeSdk(content='{"entities": []}')
    client = LlmClient(settings=_settings(llm_model="m-1"), sdk=sdk)
    out = client.complete(ChatRequest(system="sys", user="usr"))
    assert out == '{"entities": []}'
    call = sdk.completions.calls[0]
    assert call["model"] == "m-1"
    assert call["temperature"] == 0.0
    assert call["messages"][0] == {"role": "system", "content": "sys"}
    assert call["messages"][1] == {"role": "user", "content": "usr"}


@pytest.mark.unit
def test_model_override_per_request():
    sdk = _FakeSdk(content="ok")
    client = LlmClient(settings=_settings(llm_model="default"), sdk=sdk)
    client.complete(ChatRequest(system="s", user="u", model="other"))
    assert sdk.completions.calls[0]["model"] == "other"


@pytest.mark.unit
def test_empty_content_raises():
    client = LlmClient(settings=_settings(), sdk=_FakeSdk(content=None))
    with pytest.raises(PromptNerError) as exc:
        client.complete(ChatRequest(system="s", user="u"))
    assert exc.value.code is ErrorCode.LLM_EMPTY_RESPONSE


@pytest.mark.unit
def test_sdk_error_is_wrapped():
    client = LlmClient(settings=_settings(), sdk=_FakeSdk(error=RuntimeError("boom")))
    with pytest.raises(PromptNerError) as exc:
        client.complete(ChatRequest(system="s", user="u"))
    assert exc.value.code is ErrorCode.LLM_REQUEST_FAILED
    assert isinstance(exc.value.__cause__, RuntimeError)


@pytest.mark.unit
def test_call_budget_enforced():
    sdk = _FakeSdk(content="x")
    client = LlmClient(settings=_settings(max_llm_calls_per_run=2), sdk=sdk)
    client.complete(ChatRequest(system="s", user="u"))
    client.complete(ChatRequest(system="s", user="u"))
    with pytest.raises(PromptNerError) as exc:
        client.complete(ChatRequest(system="s", user="u"))
    assert exc.value.code is ErrorCode.LLM_BUDGET_EXCEEDED
    assert client.calls_made == 2


@pytest.mark.unit
def test_list_model_ids_sorted():
    sdk = _FakeSdk(model_ids=["qwen", "llama-3.1", "mistral"])
    assert list_model_ids(sdk) == ["llama-3.1", "mistral", "qwen"]
