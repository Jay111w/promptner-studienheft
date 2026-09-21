"""Unit-Tests fuer die Konfiguration / .env-Aufloesung."""

import pytest

from korrektor.config.settings import Settings, resolve_env_file, user_config_dir
from korrektor.errors import ConfigError, ErrorCode


@pytest.mark.unit
def test_resolve_env_file_prefers_user_config(tmp_path, monkeypatch):
    # Stabiler Benutzerordner hat Vorrang.
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    cfg_dir = user_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    env = cfg_dir / ".env"
    env.write_text("OPENAI_API_KEY=abc\n", encoding="utf-8")
    assert resolve_env_file() == str(env)


@pytest.mark.unit
def test_resolve_env_file_prefers_cwd_when_no_user_config(tmp_path, monkeypatch):
    # Benutzerordner leer -> Arbeitsverzeichnis wird genutzt.
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "leer_appdata"))
    work = tmp_path / "work"
    work.mkdir()
    env = work / ".env"
    env.write_text("OPENAI_API_KEY=abc\n", encoding="utf-8")
    monkeypatch.chdir(work)
    assert resolve_env_file() == str(env)


@pytest.mark.unit
def test_resolve_env_file_falls_back(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "leer_appdata"))
    monkeypatch.chdir(tmp_path)  # kein .env vorhanden
    # Faellt auf Projektstamm/Default zurueck (kein Crash).
    assert resolve_env_file().endswith(".env")


@pytest.mark.unit
def test_settings_reads_key_with_bom(tmp_path, monkeypatch):
    # Notepad speichert oft mit BOM -> darf den Key nicht zerstoeren.
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=sk-test-123\n", encoding="utf-8-sig")
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=str(env))
    assert settings.has_api_key is True
    assert settings.require_api_key() == "sk-test-123"


@pytest.mark.unit
def test_require_api_key_raises_without_key(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(_env_file=str(tmp_path / "nicht_da.env"))
    with pytest.raises(ConfigError) as exc:
        settings.require_api_key()
    assert exc.value.code is ErrorCode.MISSING_API_KEY
