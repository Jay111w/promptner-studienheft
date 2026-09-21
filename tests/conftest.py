"""Gemeinsame Pytest-Fixtures und Test-Setup."""

import os

# Qt headless betreiben (kein Fenster waehrend der Tests / in der CI).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(autouse=True)
def _isolate_settings_cache(monkeypatch):
    """Settings-Caches pro Test leeren; kein echter Key darf in Tests wirken."""
    from korrektor.config.settings import get_settings as korrektor_settings
    from promptner.config.settings import get_settings as promptner_settings

    monkeypatch.delenv("KISSKI_API_KEY", raising=False)
    korrektor_settings.cache_clear()
    promptner_settings.cache_clear()
    yield
    korrektor_settings.cache_clear()
    promptner_settings.cache_clear()
