"""Anwendungskonfiguration.

Liest ausschliesslich aus Umgebungsvariablen bzw. der lokalen ``.env``.
Der API-Key wird NIE im Code hinterlegt und NIE geloggt.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from korrektor.errors import ConfigError, ErrorCode

_APP_DIRNAME = "Studienheft-Korrektor"


def user_config_dir() -> Path:
    """Stabiler, beschreibbarer Ordner fuer die Benutzerkonfiguration.

    Auf Windows unter ``%LOCALAPPDATA%``, sonst unter dem Home-Verzeichnis.
    Dieser Ort wird von App-Neubauten NICHT ueberschrieben.
    """
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / _APP_DIRNAME


def resolve_env_file() -> str:
    """Findet die ``.env`` zuverlaessig, unabhaengig vom Arbeitsverzeichnis.

    Sucht der Reihe nach:
      1. im stabilen Benutzer-Konfigurationsordner (ueberlebt Neubauten),
      2. neben der ausfuehrbaren Datei (gebuendelte App),
      3. im aktuellen Arbeitsverzeichnis,
      4. im Projektstamm (Entwicklung).
    Gibt den ersten existierenden Pfad zurueck, sonst ``".env"``.
    """
    candidates: list[Path] = [user_config_dir() / ".env"]
    if getattr(sys, "frozen", False):  # PyInstaller-Bundle
        candidates.append(Path(sys.executable).resolve().parent / ".env")
    candidates.append(Path.cwd() / ".env")
    candidates.append(Path(__file__).resolve().parents[3] / ".env")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return ".env"


class Settings(BaseSettings):
    """Typsichere Konfiguration, gespeist aus der ``.env``."""

    model_config = SettingsConfigDict(
        env_file=resolve_env_file(),
        env_file_encoding="utf-8-sig",  # entfernt ein evtl. BOM (Notepad)
        extra="ignore",
        case_sensitive=False,
    )

    # --- OpenAI ---
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_model: str = Field(default="gpt-4o")
    openai_timeout_seconds: int = Field(default=60, ge=1)

    # --- Analyse ---
    max_chars_per_segment: int = Field(default=12_000, ge=500)

    # --- Logging ---
    log_level: str = Field(default="INFO")
    log_dir: str = Field(default="logs")

    @property
    def has_api_key(self) -> bool:
        """True, wenn ein nicht-leerer API-Key vorhanden ist."""
        return bool(self.openai_api_key.get_secret_value().strip())

    def require_api_key(self) -> str:
        """Gibt den API-Key zurueck oder wirft einen klaren Konfigurationsfehler.

        Raises:
            ConfigError: Wenn kein API-Key gesetzt ist.
        """
        key = self.openai_api_key.get_secret_value().strip()
        if not key:
            raise ConfigError(ErrorCode.MISSING_API_KEY)
        return key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Liefert die (gecachte) Konfiguration der Anwendung."""
    return Settings()
