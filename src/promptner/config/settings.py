"""Konfiguration des promptner-Pakets.

Liest ausschliesslich aus Umgebungsvariablen bzw. der lokalen ``.env``.
Der KISSKI-Key wird NIE im Code hinterlegt und NIE geloggt (``SecretStr``).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from promptner.errors import ConfigError, ErrorCode

KISSKI_BASE_URL = "https://chat-ai.academiccloud.de/v1"


class Settings(BaseSettings):
    """Typsichere Konfiguration, gespeist aus der ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM-Endpunkt (KISSKI / GWDG, OpenAI-kompatibel; siehe Woche 10) ---
    kisski_api_key: SecretStr = Field(default=SecretStr(""))
    llm_base_url: str = Field(default=KISSKI_BASE_URL)
    llm_model: str = Field(default="meta-llama-3.1-8b-instruct")
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_seed: int | None = Field(default=42)
    llm_timeout_seconds: int = Field(default=120, ge=1)
    llm_max_workers: int = Field(default=4, ge=1, le=16)
    # Drossel unterhalb der KISSKI-Limits (30/min, 200/h, 1000/Tag, 3000/Monat je Key)
    llm_calls_per_minute: int = Field(default=28, ge=1)
    llm_calls_per_hour: int = Field(default=190, ge=1)

    # --- Schutz gegen weglaufende Experimente ---
    # Notbremse je Prozess (ein `promptner run` = mehrere Laeufe); Budget steuert die Drossel
    max_llm_calls_per_run: int = Field(default=2500, gt=0)

    # --- Cache / Ergebnisse ---
    cache_dir: str = Field(default=".cache/llm")
    results_dir: str = Field(default="results")

    # --- Logging ---
    log_level: str = Field(default="INFO")
    log_dir: str = Field(default="logs")

    @property
    def has_api_key(self) -> bool:
        return bool(self.kisski_api_key.get_secret_value().strip())

    def require_api_key(self) -> str:
        key = self.kisski_api_key.get_secret_value().strip()
        if not key:
            raise ConfigError(ErrorCode.MISSING_API_KEY)
        return key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
