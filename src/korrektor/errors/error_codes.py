"""Zentrale Fehlercodes.

Schema:  KOR-<BEREICH>-<NNN>
Jeder Code ist eindeutig, nachvollziehbar und wird in Logs, UI-Meldungen
und Exceptions verwendet, damit Fehler reproduzierbar zugeordnet werden koennen.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """Eindeutige Fehlercodes der Anwendung."""

    # --- Allgemein (GEN) ---
    UNKNOWN = "KOR-GEN-001"
    INVALID_INPUT = "KOR-GEN-002"

    # --- Konfiguration (CFG) ---
    MISSING_API_KEY = "KOR-CFG-001"
    INVALID_CONFIG = "KOR-CFG-002"

    # --- PDF-Verarbeitung (PDF) ---
    PDF_NOT_FOUND = "KOR-PDF-001"
    PDF_READ_FAILED = "KOR-PDF-002"
    PDF_PAGE_OUT_OF_RANGE = "KOR-PDF-003"
    PDF_ANNOTATION_FAILED = "KOR-PDF-004"

    # --- KI / OpenAI (AI) ---
    AI_CONNECTION_FAILED = "KOR-AI-001"
    AI_TIMEOUT = "KOR-AI-002"
    AI_RESPONSE_INVALID = "KOR-AI-003"
    AI_RATE_LIMIT = "KOR-AI-004"

    # --- Analyse (ANL) ---
    SEGMENT_TOO_LARGE = "KOR-ANL-001"
    ANALYSIS_FAILED = "KOR-ANL-002"

    # --- Export (EXP) ---
    WORD_EXPORT_FAILED = "KOR-EXP-001"
    PDF_EXPORT_FAILED = "KOR-EXP-002"
    CHANGELOG_EXPORT_FAILED = "KOR-EXP-003"

    @property
    def description(self) -> str:
        """Menschenlesbare Standardbeschreibung des Fehlercodes."""
        return _DESCRIPTIONS.get(self, "Unbekannter Fehler.")


_DESCRIPTIONS: dict[ErrorCode, str] = {
    ErrorCode.UNKNOWN: "Ein unerwarteter Fehler ist aufgetreten.",
    ErrorCode.INVALID_INPUT: "Ungueltige Eingabe.",
    ErrorCode.MISSING_API_KEY: "Kein OpenAI-API-Key gefunden. Bitte .env pruefen.",
    ErrorCode.INVALID_CONFIG: "Die Konfiguration ist ungueltig.",
    ErrorCode.PDF_NOT_FOUND: "Die PDF-Datei wurde nicht gefunden.",
    ErrorCode.PDF_READ_FAILED: "Die PDF-Datei konnte nicht gelesen werden.",
    ErrorCode.PDF_PAGE_OUT_OF_RANGE: "Der gewaehlte Seitenbereich liegt ausserhalb des Dokuments.",
    ErrorCode.PDF_ANNOTATION_FAILED: "Eine Annotation konnte nicht ins PDF geschrieben werden.",
    ErrorCode.AI_CONNECTION_FAILED: "Verbindung zur OpenAI-API fehlgeschlagen.",
    ErrorCode.AI_TIMEOUT: "Zeitueberschreitung bei der OpenAI-Anfrage.",
    ErrorCode.AI_RESPONSE_INVALID: "Die Antwort der KI konnte nicht verarbeitet werden.",
    ErrorCode.AI_RATE_LIMIT: "Rate-Limit der OpenAI-API erreicht.",
    ErrorCode.SEGMENT_TOO_LARGE: "Das Segment ist zu gross fuer eine Anfrage.",
    ErrorCode.ANALYSIS_FAILED: "Die Analyse ist fehlgeschlagen.",
    ErrorCode.WORD_EXPORT_FAILED: "Der Word-Export ist fehlgeschlagen.",
    ErrorCode.PDF_EXPORT_FAILED: "Der PDF-Export ist fehlgeschlagen.",
    ErrorCode.CHANGELOG_EXPORT_FAILED: "Das Aenderungs-PDF konnte nicht erstellt werden.",
}
