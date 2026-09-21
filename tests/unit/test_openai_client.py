"""Unit-Tests fuer den OpenAI-Client (mit Fake-Client, ohne echten Key)."""

from types import SimpleNamespace

import pytest

from korrektor.errors import AiError, ErrorCode
from korrektor.services.ai.openai_client import OpenAiClient


class _FakeCompletions:
    def __init__(self, content=None, error=None):
        self._content = content
        self._error = error

    def create(self, **kwargs):
        if self._error is not None:
            raise self._error
        message = SimpleNamespace(content=self._content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class _FakeModels:
    def __init__(self, error=None):
        self._error = error

    def list(self):
        if self._error is not None:
            raise self._error
        return SimpleNamespace(data=[])


class _FakeClient:
    def __init__(self, content=None, error=None, models_error=None):
        self.chat = SimpleNamespace(completions=_FakeCompletions(content, error))
        self.models = _FakeModels(models_error)


# Exceptions mit denselben Klassennamen wie die OpenAI-SDK-Fehler.
class RateLimitError(Exception):
    pass


class APITimeoutError(Exception):
    pass


@pytest.mark.unit
def test_complete_json_returns_content():
    client = OpenAiClient(client=_FakeClient(content='{"corrections": []}'))
    assert client.complete_json("sys", "user") == '{"corrections": []}'


@pytest.mark.unit
def test_empty_content_raises_invalid():
    client = OpenAiClient(client=_FakeClient(content=None))
    with pytest.raises(AiError) as exc:
        client.complete_json("sys", "user")
    assert exc.value.code is ErrorCode.AI_RESPONSE_INVALID


@pytest.mark.unit
def test_rate_limit_mapped():
    client = OpenAiClient(client=_FakeClient(error=RateLimitError("slow down")))
    with pytest.raises(AiError) as exc:
        client.complete_json("sys", "user")
    assert exc.value.code is ErrorCode.AI_RATE_LIMIT


@pytest.mark.unit
def test_timeout_mapped():
    client = OpenAiClient(client=_FakeClient(error=APITimeoutError("timeout")))
    with pytest.raises(AiError) as exc:
        client.complete_json("sys", "user")
    assert exc.value.code is ErrorCode.AI_TIMEOUT


@pytest.mark.unit
def test_unknown_error_maps_to_connection_failed():
    client = OpenAiClient(client=_FakeClient(error=ValueError("boom")))
    with pytest.raises(AiError) as exc:
        client.complete_json("sys", "user")
    assert exc.value.code is ErrorCode.AI_CONNECTION_FAILED


@pytest.mark.unit
def test_verify_connection_ok():
    client = OpenAiClient(client=_FakeClient())
    assert client.verify_connection() is True


@pytest.mark.unit
def test_verify_connection_auth_error_mapped():
    class AuthenticationError(Exception):
        pass

    client = OpenAiClient(client=_FakeClient(models_error=AuthenticationError("bad key")))
    with pytest.raises(AiError) as exc:
        client.verify_connection()
    assert exc.value.code is ErrorCode.AI_CONNECTION_FAILED
