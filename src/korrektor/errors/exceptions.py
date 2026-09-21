"""Strukturierte Exception-Hierarchie.

Alle anwendungsspezifischen Fehler erben von :class:`KorrektorError` und
tragen einen :class:`ErrorCode`. So lassen sich Fehler einheitlich loggen,
im UI anzeigen und in Tests gezielt pruefen.
"""

from __future__ import annotations

from typing import Any

from korrektor.errors.error_codes import ErrorCode


class KorrektorError(Exception):
    """Basisklasse fuer alle Anwendungsfehler.

    Args:
        code: Eindeutiger Fehlercode.
        message: Optionale, kontextspezifische Meldung. Faellt auf die
            Standardbeschreibung des Codes zurueck.
        context: Zusaetzliche Diagnose-Daten (z. B. Dateiname, Seitenzahl).
        cause: Urspruengliche Ausnahme, falls vorhanden.
    """

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
        """Serialisierbare Darstellung fuer Logging und UI."""
        return {
            "code": self.code.value,
            "message": self.message,
            "context": self.context,
        }


class ConfigError(KorrektorError):
    """Fehler in der Konfiguration (z. B. fehlender API-Key)."""


class PdfError(KorrektorError):
    """Fehler beim Lesen oder Annotieren von PDF-Dateien."""


class AiError(KorrektorError):
    """Fehler bei der Kommunikation mit der OpenAI-API."""


class AnalysisError(KorrektorError):
    """Fehler waehrend der Korrektur-Analyse."""


class ExportError(KorrektorError):
    """Fehler beim Export (Word, PDF, Changelog)."""
