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


# Exceptions mit denselben Klassennamen wie im OpenAI-SDK (Mapping erfolgt per Name).
class RateLimitError(Exception):
    pass


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
def test_fewshot_turns_are_sent_as_alternating_messages():
    sdk = _FakeSdk(content="ok")
    client = LlmClient(settings=_settings(), sdk=sdk)
    req = ChatRequest(system="sys", user="final", turns=(("q1", "a1"), ("q2", "a2")))
    client.complete(req)
    assert sdk.completions.calls[0]["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "q1"},
        {"role": "assistant", "content": "a1"},
        {"role": "user", "content": "q2"},
        {"role": "assistant", "content": "a2"},
        {"role": "user", "content": "final"},
    ]
    assert req.full_text == "sys\n\nq1\n\na1\n\nq2\n\na2\n\nfinal"


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


class _FlakyCompletions:
    """Wirft n-mal RateLimitError, dann Erfolg."""

    def __init__(self, failures: int, content: str):
        self.failures, self._content, self.calls = failures, content, 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise RateLimitError("slow down")
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


@pytest.mark.unit
def test_rate_limit_is_retried_with_backoff(monkeypatch):
    from promptner.llm import client as client_module

    monkeypatch.setattr(client_module, "_BACKOFF_WAIT_SECONDS", 0)
    flaky = _FlakyCompletions(failures=2, content="ok")
    sdk = SimpleNamespace(chat=SimpleNamespace(completions=flaky), models=_FakeModels([]))
    client = LlmClient(settings=_settings(), sdk=sdk)
    assert client.complete(ChatRequest(system="s", user="u")) == "ok"
    assert flaky.calls == 3
    assert client.calls_made == 1  # ein logischer Aufruf, drei physische Versuche


@pytest.mark.unit
def test_rate_limit_gives_up_after_max_attempts(monkeypatch):
    from promptner.llm import client as client_module

    monkeypatch.setattr(client_module, "_BACKOFF_WAIT_SECONDS", 0)
    monkeypatch.setattr(client_module, "_BACKOFF_ATTEMPTS", 2)
    flaky = _FlakyCompletions(failures=5, content="ok")
    sdk = SimpleNamespace(chat=SimpleNamespace(completions=flaky), models=_FakeModels([]))
    client = LlmClient(settings=_settings(), sdk=sdk)
    with pytest.raises(PromptNerError) as exc:
        client.complete(ChatRequest(system="s", user="u"))
    assert exc.value.code is ErrorCode.LLM_RATE_LIMITED
    assert flaky.calls == 2


def _rate_limit_with_retry_after(seconds: str) -> RateLimitError:
    """Wie das OpenAI-SDK: ``response.headers`` traegt ``retry-after`` in Sekunden."""
    exc = RateLimitError("API rate limit exceeded")
    exc.response = SimpleNamespace(headers={"retry-after": seconds})
    return exc


@pytest.mark.unit
def test_rate_limit_waits_for_retry_after_header(monkeypatch):
    from promptner.llm import client as client_module

    slept: list[float] = []
    monkeypatch.setattr(client_module, "_sleep", slept.append)
    calls = {"n": 0}

    def create(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise _rate_limit_with_retry_after("1035")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    sdk = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)), models=_FakeModels([])
    )
    client = LlmClient(settings=_settings(), sdk=sdk)
    assert client.complete(ChatRequest(system="s", user="u")) == "ok"
    assert slept and slept[0] >= 1035  # Endpunkt-Angabe wird respektiert, nicht 2^n


@pytest.mark.unit
def test_throttle_sleeps_when_minute_window_is_full(monkeypatch):
    from promptner.llm import client as client_module

    clock = [1000.0]
    slept: list[float] = []

    def fake_sleep(sec):
        slept.append(sec)
        clock[0] += sec

    monkeypatch.setattr(client_module, "_now", lambda: clock[0])
    monkeypatch.setattr(client_module, "_sleep", fake_sleep)
    sdk = _FakeSdk(content="ok")
    client = LlmClient(settings=_settings(llm_calls_per_minute=2, llm_calls_per_hour=100), sdk=sdk)
    for _ in range(3):
        client.complete(ChatRequest(system="s", user="u"))
    assert len(sdk.completions.calls) == 3
    assert slept and 59 <= slept[0] <= 61  # dritter Aufruf wartet, bis der erste 60 s alt ist


@pytest.mark.unit
def test_throttle_respects_hour_window(monkeypatch):
    from promptner.llm import client as client_module

    clock = [0.0]
    slept: list[float] = []

    def fake_sleep(sec):
        slept.append(sec)
        clock[0] += sec

    monkeypatch.setattr(client_module, "_now", lambda: clock[0])
    monkeypatch.setattr(client_module, "_sleep", fake_sleep)
    sdk = _FakeSdk(content="ok")
    client = LlmClient(settings=_settings(llm_calls_per_minute=100, llm_calls_per_hour=2), sdk=sdk)
    for _ in range(3):
        client.complete(ChatRequest(system="s", user="u"))
    assert slept and 3599 <= slept[0] <= 3601
