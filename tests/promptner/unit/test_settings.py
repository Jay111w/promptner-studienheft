"""Unit-Tests fuer die promptner-Konfiguration (KISSKI-Endpunkt)."""

import pytest

from promptner.config.settings import Settings
from promptner.errors import ErrorCode, PromptNerError


@pytest.mark.unit
def test_defaults_point_to_kisski_endpoint():
    s = Settings(_env_file=None)
    assert s.llm_base_url == "https://chat-ai.academiccloud.de/v1"
    assert s.llm_model == "meta-llama-3.1-8b-instruct"
    assert s.llm_temperature == 0.0
    assert s.has_api_key is False


@pytest.mark.unit
def test_api_key_from_env(monkeypatch):
    monkeypatch.setenv("KISSKI_API_KEY", "abc123")
    s = Settings(_env_file=None)
    assert s.has_api_key is True
    assert s.require_api_key() == "abc123"


@pytest.mark.unit
def test_missing_key_raises_config_error():
    s = Settings(_env_file=None)
    with pytest.raises(PromptNerError) as exc:
        s.require_api_key()
    assert exc.value.code is ErrorCode.MISSING_API_KEY


@pytest.mark.unit
def test_secret_never_in_repr(monkeypatch):
    monkeypatch.setenv("KISSKI_API_KEY", "topsecret")
    s = Settings(_env_file=None)
    assert "topsecret" not in repr(s)
    assert "topsecret" not in str(s.model_dump())


@pytest.mark.unit
def test_call_budget_must_be_positive():
    with pytest.raises(ValueError):
        Settings(_env_file=None, max_llm_calls_per_run=0)
