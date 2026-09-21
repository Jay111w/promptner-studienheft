"""Duenner, fehlerbehandelnder Client fuer den OpenAI-kompatiblen KISSKI-Endpunkt.

Der echte SDK-Client wird lazy erzeugt; fuer Tests laesst sich ein beliebiges
Objekt mit ``chat.completions.create`` und ``models.list`` injizieren.
Ein Aufruf-Deckel (``max_llm_calls_per_run``) verhindert weglaufende Experimente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from promptner.config import get_logger
from promptner.config.settings import Settings, get_settings
from promptner.errors import ErrorCode, LlmError

log = get_logger("llm.client")


class ChatSdk(Protocol):
    """Minimales Protokoll, das der OpenAI-Client erfuellt (fuer Fakes)."""

    @property
    def chat(self) -> Any: ...  # pragma: no cover

    @property
    def models(self) -> Any: ...  # pragma: no cover


@dataclass(frozen=True)
class ChatRequest:
    """Eine Chat-Anfrage; ``model`` ueberschreibt das Standardmodell."""

    system: str
    user: str
    model: str | None = None
    json_mode: bool = False


class LlmClient:
    def __init__(self, settings: Settings | None = None, sdk: ChatSdk | None = None) -> None:
        self._settings = settings or get_settings()
        self._sdk = sdk
        self.calls_made = 0

    def _ensure_sdk(self) -> ChatSdk:
        if self._sdk is None:
            from openai import OpenAI  # lazy: Tests brauchen das SDK nicht

            self._sdk = OpenAI(
                base_url=self._settings.llm_base_url,
                api_key=self._settings.require_api_key(),
                timeout=self._settings.llm_timeout_seconds,
            )
        return self._sdk

    def complete(self, request: ChatRequest) -> str:
        """Sendet eine Chat-Anfrage und liefert den Antworttext.

        Raises:
            LlmError: Bei Budget-Ueberschreitung, SDK-Fehlern oder leerer Antwort.
        """
        if self.calls_made >= self._settings.max_llm_calls_per_run:
            raise LlmError(
                ErrorCode.LLM_BUDGET_EXCEEDED,
                context={"limit": self._settings.max_llm_calls_per_run},
            )
        sdk = self._ensure_sdk()
        kwargs: dict[str, Any] = {
            "model": request.model or self._settings.llm_model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user},
            ],
            "temperature": self._settings.llm_temperature,
        }
        if self._settings.llm_seed is not None:
            kwargs["seed"] = self._settings.llm_seed
        if request.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        self.calls_made += 1
        try:
            response = sdk.chat.completions.create(**kwargs)
        except Exception as exc:  # noqa: BLE001 - in LlmError uebersetzen
            code = (
                ErrorCode.LLM_RATE_LIMITED
                if type(exc).__name__ == "RateLimitError"
                else ErrorCode.LLM_REQUEST_FAILED
            )
            log.error("LLM-Anfrage fehlgeschlagen: %s (%s)", code.value, type(exc).__name__)
            raise LlmError(code, cause=exc) from exc

        content = response.choices[0].message.content
        if not content:
            raise LlmError(ErrorCode.LLM_EMPTY_RESPONSE)
        return content


def list_model_ids(sdk: ChatSdk) -> list[str]:
    """Sortierte Liste der am Endpunkt verfuegbaren Modell-IDs."""
    return sorted(m.id for m in sdk.models.list().data)
