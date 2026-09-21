"""Anbindung an die OpenAI-API.

Der API-Key wird ausschliesslich ueber :mod:`korrektor.config.settings`
(also aus der lokalen ``.env``) bezogen und niemals geloggt. Der eigentliche
OpenAI-Client wird erst bei Bedarf erzeugt; fuer Tests kann ein beliebiger
kompatibler Client injiziert werden.
"""

from __future__ import annotations

from typing import Protocol

from korrektor.config import get_logger, get_settings
from korrektor.config.settings import Settings
from korrektor.errors import AiError, ErrorCode

log = get_logger("services.ai.openai_client")


class ChatClient(Protocol):
    """Minimales Protokoll, das der OpenAI-Client erfuellt (fuer Mocking)."""

    @property
    def chat(self): ...  # pragma: no cover - reine Typ-Deklaration


# Klassennamen der OpenAI-Fehler -> eigene Fehlercodes.
# (Per Namensvergleich, damit dieses Modul ohne openai-Import testbar bleibt.)
_ERROR_CODE_BY_NAME: dict[str, ErrorCode] = {
    "APITimeoutError": ErrorCode.AI_TIMEOUT,
    "RateLimitError": ErrorCode.AI_RATE_LIMIT,
    "APIConnectionError": ErrorCode.AI_CONNECTION_FAILED,
    "AuthenticationError": ErrorCode.AI_CONNECTION_FAILED,
}


class OpenAiClient:
    """Duenne, fehlerbehandelnde Huelle um den OpenAI-Chat-Client."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: ChatClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client

    def _ensure_client(self) -> ChatClient:
        """Erzeugt den echten OpenAI-Client lazy (Key aus .env)."""
        if self._client is None:
            key = self._settings.require_api_key()  # wirft bei fehlendem Key
            from openai import OpenAI  # lazy import

            self._client = OpenAI(
                api_key=key,
                timeout=self._settings.openai_timeout_seconds,
            )
        return self._client

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """Sendet eine Chat-Anfrage im JSON-Modus und liefert den Rohtext.

        Raises:
            AiError: Bei Verbindungs-, Timeout-, Rate-Limit- oder sonstigen
                API-Fehlern bzw. wenn keine Antwort geliefert wurde.
        """
        client = self._ensure_client()
        try:
            response = client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
        except Exception as exc:  # noqa: BLE001 - in AiError uebersetzen
            code = _ERROR_CODE_BY_NAME.get(type(exc).__name__, ErrorCode.AI_CONNECTION_FAILED)
            log.error("OpenAI-Anfrage fehlgeschlagen: %s", code.value)
            raise AiError(code, cause=exc) from exc

        content = response.choices[0].message.content
        if not content:
            raise AiError(ErrorCode.AI_RESPONSE_INVALID, "Leere Antwort der KI.")
        return content

    def verify_connection(self) -> bool:
        """Prueft Schluessel und Erreichbarkeit der API (ruft ``models.list``).

        Returns:
            True bei erfolgreicher Verbindung.

        Raises:
            AiError: Bei Authentifizierungs-/Verbindungsfehlern.
        """
        client = self._ensure_client()
        try:
            client.models.list()
        except Exception as exc:  # noqa: BLE001
            code = _ERROR_CODE_BY_NAME.get(type(exc).__name__, ErrorCode.AI_CONNECTION_FAILED)
            raise AiError(code, cause=exc) from exc
        return True
