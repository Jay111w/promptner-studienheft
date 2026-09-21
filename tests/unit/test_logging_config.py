"""Unit-Tests fuer die Logging-Konfiguration."""

import logging
from pathlib import Path

import pytest

from korrektor.config.logging_config import resolve_log_dir, setup_logging


@pytest.mark.unit
def test_absolute_log_dir_is_used_as_is(tmp_path):
    target = tmp_path / "meine_logs"
    assert resolve_log_dir(str(target)) == target


@pytest.mark.unit
def test_relative_log_dir_goes_to_user_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    resolved = resolve_log_dir("logs")
    assert resolved == tmp_path / "Studienheft-Korrektor" / "logs"


@pytest.mark.unit
def test_setup_logging_creates_file(tmp_path):
    log = setup_logging(level="INFO", log_dir=str(tmp_path / "logs"))
    log.info("Testeintrag")
    assert (tmp_path / "logs" / "korrektor.log").is_file()


@pytest.mark.unit
def test_setup_logging_survives_unwritable_dir(monkeypatch, tmp_path):
    # mkdir schlaegt fehl -> App darf nicht crashen, Konsole bleibt aktiv.
    def boom(*args, **kwargs):
        raise PermissionError("Zugriff verweigert")

    monkeypatch.setattr(Path, "mkdir", boom)
    log = setup_logging(level="INFO", log_dir=str(tmp_path / "logs"))
    # Es existiert weiterhin mindestens der Konsolen-Handler.
    assert any(isinstance(h, logging.StreamHandler) for h in log.handlers)
