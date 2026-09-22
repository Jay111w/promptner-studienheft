"""Duenner, fehlerbehandelnder Client fuer den OpenAI-kompatiblen KISSKI-Endpunkt.

Der echte SDK-Client wird lazy erzeugt; fuer Tests laesst sich ein beliebiges
Objekt mit ``chat.completions.create`` und ``models.list`` injizieren.
Ein Aufruf-Deckel (``max_llm_calls_per_run``) verhindert weglaufende Experimente.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Protocol

from promptner.config import get_logger
from promptner.config.settings import Settings, get_settings
from promptner.errors import ErrorCode, LlmError

log = get_logger("llm.client")

# Backoff-Parameter (Tests setzen sie per monkeypatch herab).
_BACKOFF_ATTEMPTS = 8
_BACKOFF_WAIT_SECONDS = 2
_MAX_WAIT_SECONDS = 3700  # KISSKI nennt bei Stundenlimit bis zu ~3600 s retry-after
_RETRYABLE = {"RateLimitError", "APIConnectionError", "APITimeoutError", "InternalServerError"}

# Uhr und Schlaf als Modulfunktionen, damit Tests sie ersetzen koennen.
_now = time.monotonic
_sleep = time.sleep


def _is_retryable(exc: BaseException) -> bool:
    return type(exc).__name__ in _RETRYABLE


def _retry_after_seconds(exc: BaseException) -> float | None:
    """``retry-after`` aus der 429-Antwort, falls das SDK sie mitliefert."""
    headers = getattr(getattr(exc, "response", None), "headers", None)
    if not headers:
        return None
    value = headers.get("retry-after")  # ratelimit-reset kann ein Zeitstempel sein - ignorieren
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


class _RateWindows:
    """Haelt Aufrufe unter Minuten- und Stundenlimit; blockiert sonst bis Platz ist."""

    def __init__(self, per_minute: int, per_hour: int) -> None:
        self._limits = ((60.0, per_minute, deque()), (3600.0, per_hour, deque()))
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = _now()
                wait = 0.0
                for span, cap, stamps in self._limits:
                    while stamps and now - stamps[0] >= span:
                        stamps.popleft()
                    if len(stamps) >= cap:
                        wait = max(wait, span - (now - stamps[0]))
                if wait <= 0:
                    for _, _, stamps in self._limits:
                        stamps.append(now)
                    return
            log.info("Drossel: warte %.0f s (Endpunkt-Limit)", wait)
            _sleep(wait + 0.05)


class ChatSdk(Protocol):
    """Minimales Protokoll, das der OpenAI-Client erfuellt (fuer Fakes)."""

    @property
    def chat(self) -> Any: ...  # pragma: no cover

    @property
    def models(self) -> Any: ...  # pragma: no cover


@dataclass(frozen=True)
class ChatRequest:
    """Eine Chat-Anfrage; ``model`` ueberschreibt das Standardmodell.

    ``turns`` sind Few-Shot-Beispiele als (User, Assistant)-Paare vor der eigentlichen
    ``user``-Nachricht. Chat-Modelle beantworten Beispiele, die alle in einer Nachricht
    stehen, sonst erneut (Echo) - als eigene Turns bleiben sie Kontext.
    """

    system: str
    user: str
    model: str | None = None
    json_mode: bool = False
    turns: tuple[tuple[str, str], ...] = ()

    def messages(self) -> list[dict[str, str]]:
        out = [{"role": "system", "content": self.system}]
        for asked, answered in self.turns:
            out.append({"role": "user", "content": asked})
            out.append({"role": "assistant", "content": answered})
        out.append({"role": "user", "content": self.user})
        return out

    @property
    def full_text(self) -> str:
        """Alle Nachrichten hintereinander - fuer Cache-Schluessel, Hash und Tests."""
        return "\n\n".join(m["content"] for m in self.messages())


class LlmClient:
    def __init__(self, settings: Settings | None = None, sdk: ChatSdk | None = None) -> None:
        self._settings = settings or get_settings()
        self._sdk = sdk
        self.calls_made = 0
        self._windows = _RateWindows(
            self._settings.llm_calls_per_minute, self._settings.llm_calls_per_hour
        )
        self._lock = threading.Lock()

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
        with self._lock:
            if self.calls_made >= self._settings.max_llm_calls_per_run:
                raise LlmError(
                    ErrorCode.LLM_BUDGET_EXCEEDED,
                    context={"limit": self._settings.max_llm_calls_per_run},
                )
            self.calls_made += 1
            sdk = self._ensure_sdk()
        kwargs: dict[str, Any] = {
            "model": request.model or self._settings.llm_model,
            "messages": request.messages(),
            "temperature": self._settings.llm_temperature,
        }
        if self._settings.llm_seed is not None:
            kwargs["seed"] = self._settings.llm_seed
        if request.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self._create_with_backoff(sdk, kwargs, self._windows)
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

    @staticmethod
    def _create_with_backoff(sdk: ChatSdk, kwargs: dict[str, Any], windows: _RateWindows) -> Any:
        """Drosselt vorab und wiederholt bei Rate-Limit/Verbindungsfehlern.

        Bei 429 zaehlt die ``retry-after``-Angabe des Endpunkts (bis zu einer Stunde),
        sonst exponentielles Warten.
        """
        for attempt in range(1, _BACKOFF_ATTEMPTS + 1):
            windows.acquire()
            try:
                return sdk.chat.completions.create(**kwargs)
            except Exception as exc:  # noqa: BLE001 - nur bekannte Fehler wiederholen
                if not _is_retryable(exc) or attempt == _BACKOFF_ATTEMPTS:
                    raise
                wait = _retry_after_seconds(exc)
                if wait is None:
                    wait = min(_BACKOFF_WAIT_SECONDS * 2 ** (attempt - 1), 60)
                wait = min(wait + 1, _MAX_WAIT_SECONDS)
                log.warning(
                    "LLM-Anfrage: %s, Versuch %d/%d in %.0f s",
                    type(exc).__name__,
                    attempt + 1,
                    _BACKOFF_ATTEMPTS,
                    wait,
                )
                _sleep(wait)
        raise RuntimeError("unreachable")  # pragma: no cover


def list_model_ids(sdk: ChatSdk) -> list[str]:
    """Sortierte Liste der am Endpunkt verfuegbaren Modell-IDs."""
    return sorted(m.id for m in sdk.models.list().data)
