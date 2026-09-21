"""Zentrale Fehlerbehandlung: Fehlercodes und strukturierte Exceptions."""

from korrektor.errors.error_codes import ErrorCode
from korrektor.errors.exceptions import (
    AiError,
    AnalysisError,
    ConfigError,
    ExportError,
    KorrektorError,
    PdfError,
)

__all__ = [
    "ErrorCode",
    "KorrektorError",
    "ConfigError",
    "PdfError",
    "AiError",
    "AnalysisError",
    "ExportError",
]
