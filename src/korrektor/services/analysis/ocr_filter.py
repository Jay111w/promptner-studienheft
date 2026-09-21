"""Filtert reine OCR-/Export-Trennungsartefakte heraus.

Zweite Verteidigungslinie zusaetzlich zur Prompt-Regel: Verwirft Korrekturen,
die lediglich ein durch den PDF-Export getrenntes Wort wieder zusammenfuegen
(z. B. "Veroeffentlichungs-kanaele" -> "Veroeffentlichungskanaele").
"""

from __future__ import annotations

import re

from korrektor.config import get_logger
from korrektor.domain import ActionType, Correction

log = get_logger("services.analysis.ocr_filter")

# Bindestrich (auch weiches Trennzeichen) ggf. mit Umbruch/Whitespace.
_HYPHEN_BREAK = re.compile(r"[­\-]\s*")


def _dehyphenate(text: str) -> str:
    """Entfernt Trennstriche samt folgendem Whitespace/Umbruch."""
    return _HYPHEN_BREAK.sub("", text)


def is_ocr_hyphenation_only(correction: Correction) -> bool:
    """True, wenn die Korrektur nur eine Export-Trennung rueckgaengig macht."""
    if correction.action_type is not ActionType.REPLACE:
        return False
    original = correction.original_text
    corrected = correction.corrected_text
    if "-" not in original and "­" not in original:
        return False
    # Reines Zusammenfuegen: ohne Trennstriche sind beide identisch.
    return _dehyphenate(original) == _dehyphenate(corrected)


def filter_ocr_artifacts(
    corrections: list[Correction],
) -> list[Correction]:
    """Gibt die Korrekturen ohne reine Trennungsartefakte zurueck."""
    kept: list[Correction] = []
    dropped = 0
    for c in corrections:
        if is_ocr_hyphenation_only(c):
            dropped += 1
            continue
        kept.append(c)
    if dropped:
        log.info("%d OCR-Trennungsartefakt(e) ignoriert.", dropped)
    return kept
