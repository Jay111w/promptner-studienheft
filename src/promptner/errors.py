"""Fehlercodes und Exception-Hierarchie des promptner-Pakets.

Schema: ``NER-<BEREICH>-<NNN>``. Jede Schicht uebersetzt Fremd-Exceptions in
:class:`PromptNerError`, damit Logs, CLI und Tests einheitlich pruefen koennen.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    # --- Konfiguration ---
    MISSING_API_KEY = "NER-CFG-001"
    INVALID_CONFIG = "NER-CFG-002"

    # --- Daten ---
    DATASET_NOT_FOUND = "NER-DATA-001"
    DATASET_PARSE_FAILED = "NER-DATA-002"
    INVALID_BIO_SEQUENCE = "NER-DATA-003"

    # --- LLM ---
    LLM_REQUEST_FAILED = "NER-LLM-001"
    LLM_EMPTY_RESPONSE = "NER-LLM-002"
    LLM_BUDGET_EXCEEDED = "NER-LLM-003"
    LLM_RATE_LIMITED = "NER-LLM-004"

    # --- Prompt / Parsing ---
    RESPONSE_INVALID = "NER-PARSE-001"
    SPAN_NOT_IN_SENTENCE = "NER-PARSE-002"

    # --- Evaluation ---
    EVAL_FAILED = "NER-EVAL-001"

    @property
    def description(self) -> str:
        return _DESCRIPTIONS.get(self, "Unbekannter Fehler.")


_DESCRIPTIONS: dict[ErrorCode, str] = {
    ErrorCode.MISSING_API_KEY: "Kein KISSKI_API_KEY gefunden. Bitte .env pruefen.",
    ErrorCode.INVALID_CONFIG: "Die Konfiguration ist ungueltig.",
    ErrorCode.DATASET_NOT_FOUND: "Datensatz nicht gefunden.",
    ErrorCode.DATASET_PARSE_FAILED: "Datensatz konnte nicht gelesen werden.",
    ErrorCode.INVALID_BIO_SEQUENCE: "Ungueltige BIO-Tag-Folge.",
    ErrorCode.LLM_REQUEST_FAILED: "LLM-Anfrage fehlgeschlagen.",
    ErrorCode.LLM_EMPTY_RESPONSE: "Leere Antwort vom LLM.",
    ErrorCode.LLM_BUDGET_EXCEEDED: "Aufruf-Deckel fuer diesen Lauf erreicht.",
    ErrorCode.LLM_RATE_LIMITED: "Rate-Limit des Endpunkts erreicht.",
    ErrorCode.RESPONSE_INVALID: "LLM-Antwort entspricht nicht dem Schema.",
    ErrorCode.SPAN_NOT_IN_SENTENCE: "Vorhergesagter Span kommt im Satz nicht vor.",
    ErrorCode.EVAL_FAILED: "Evaluation fehlgeschlagen.",
}


class PromptNerError(Exception):
    """Basisklasse aller promptner-Fehler; traegt einen :class:`ErrorCode`."""

    def __init__(
        self,
        code: ErrorCode,
        message: str | None = None,
        *,
        context: dict[str, Any] | None = None,
        cause: BaseException | None = None,
    ) -> None:
        self.code = code
        self.message = message or code.description
        self.context = context or {}
        super().__init__(f"[{code.value}] {self.message}")
        if cause is not None:
            self.__cause__ = cause

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "context": self.context}


class ConfigError(PromptNerError):
    """Fehler in der Konfiguration."""


class DataError(PromptNerError):
    """Fehler beim Laden oder Parsen von Datensaetzen."""


class LlmError(PromptNerError):
    """Fehler bei der Kommunikation mit dem LLM-Endpunkt."""


class ParseError(PromptNerError):
    """LLM-Antwort passt nicht zum Schema oder zum Satz."""
