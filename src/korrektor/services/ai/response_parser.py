"""Wandelt die JSON-Antwort der KI in :class:`Correction`-Objekte um.

Vergibt fortlaufende, konsistente IDs (z. B. ``K-001``) und setzt die
Seitenreferenzen (PDF + gedruckt) sowie die Suchposition (quote) fuer die
spaetere PDF-Annotation.
"""

from __future__ import annotations

import json
from typing import Any

from korrektor.config import get_logger
from korrektor.domain import (
    ActionType,
    Category,
    Correction,
    TextLocation,
    make_correction_id,
)
from korrektor.errors import AiError, ErrorCode

log = get_logger("services.ai.response_parser")

_CATEGORY_BY_VALUE = {c.value: c for c in Category}
_ACTION_BY_VALUE = {a.value: a for a in ActionType}


def parse_corrections(
    raw_json: str,
    *,
    pdf_page: int,
    printed_page: int | None = None,
    start_index: int = 1,
) -> list[Correction]:
    """Parst die KI-Antwort eines Segments in Korrektur-Objekte.

    Args:
        raw_json: Rohtext der KI (JSON-Objekt mit Schluessel ``corrections``).
        pdf_page: 0-basierter PDF-Seitenindex des geprueften Segments.
        printed_page: Zugehoerige gedruckte Heft-Seitenzahl (optional).
        start_index: Startwert fuer die fortlaufende ID-Vergabe.

    Returns:
        Liste der erkannten Korrekturen.

    Raises:
        AiError: Bei ungueltigem JSON oder unbekannten Kategorie-/Aktionswerten.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise AiError(
            ErrorCode.AI_RESPONSE_INVALID,
            "Antwort war kein gueltiges JSON.",
            cause=exc,
        ) from exc

    items = _extract_items(data)
    corrections: list[Correction] = []
    for offset, item in enumerate(items):
        corrections.append(
            _build_correction(
                item,
                index=start_index + offset,
                pdf_page=pdf_page,
                printed_page=printed_page,
            )
        )
    log.debug("%d Korrektur(en) auf PDF-Seite %d geparst.", len(corrections), pdf_page)
    return corrections


def _extract_items(data: Any) -> list[dict[str, Any]]:
    """Holt die Korrektur-Liste aus verschiedenen erlaubten Strukturen."""
    if isinstance(data, dict):
        items = data.get("corrections", [])
    elif isinstance(data, list):
        items = data
    else:
        raise AiError(
            ErrorCode.AI_RESPONSE_INVALID,
            "Unerwartete JSON-Struktur.",
            context={"type": type(data).__name__},
        )
    if not isinstance(items, list):
        raise AiError(ErrorCode.AI_RESPONSE_INVALID, "'corrections' ist keine Liste.")
    return items


def _build_correction(
    item: dict[str, Any],
    *,
    index: int,
    pdf_page: int,
    printed_page: int | None,
) -> Correction:
    original = str(item.get("original_text", "")).strip()
    category_raw = str(item.get("category", "")).strip().upper()
    action_raw = str(item.get("action_type", "")).strip().lower()

    category = _CATEGORY_BY_VALUE.get(category_raw)
    if category is None:
        raise AiError(
            ErrorCode.AI_RESPONSE_INVALID,
            f"Unbekannte Kategorie: {category_raw!r}",
            context={"index": index},
        )
    action = _ACTION_BY_VALUE.get(action_raw)
    if action is None:
        raise AiError(
            ErrorCode.AI_RESPONSE_INVALID,
            f"Unbekannter action_type: {action_raw!r}",
            context={"index": index},
        )

    return Correction(
        id=make_correction_id(index),
        pdf_page=pdf_page,
        printed_page=printed_page,
        original_text=original,
        corrected_text=str(item.get("corrected_text", "")).strip(),
        category=category,
        action_type=action,
        description=str(item.get("description", "")).strip(),
        reason=str(item.get("reason", "")).strip(),
        location=TextLocation(pdf_page=pdf_page, quote=original),
    )
