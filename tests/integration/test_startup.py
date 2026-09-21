"""Integrationstest fuer den Anwendungsstart / Selbsttest."""

import pytest

from korrektor.app import main, run_self_check


@pytest.mark.integration
def test_self_check_keys_present():
    status = run_self_check()
    assert set(status) == {
        "app_running",
        "api_configured",
        "analysis_active",
        "has_errors",
    }
    assert status["app_running"] is True
    assert status["has_errors"] is False


@pytest.mark.integration
def test_main_check_returns_zero(tmp_path, monkeypatch):
    # Logging in ein temporaeres Verzeichnis lenken.
    monkeypatch.setenv("LOG_DIR", str(tmp_path / "logs"))
    # get_settings ist gecached -> Cache leeren, damit LOG_DIR greift.
    from korrektor.config.settings import get_settings

    get_settings.cache_clear()
    # --check fuehrt nur den Selbsttest aus, ohne die GUI zu starten.
    assert main(["--check"]) == 0
