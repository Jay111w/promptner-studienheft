"""Domain-Modelle: reine Datenstrukturen ohne externe Abhaengigkeiten."""

from korrektor.domain.correction import (
    ActionType,
    Category,
    Correction,
    CorrectionStatus,
    TextLocation,
    make_correction_id,
)
from korrektor.domain.document import (
    Chapter,
    DocumentInfo,
    PageMapping,
    PageRange,
)

__all__ = [
    "Category",
    "ActionType",
    "CorrectionStatus",
    "Correction",
    "TextLocation",
    "make_correction_id",
    "PageRange",
    "Chapter",
    "PageMapping",
    "DocumentInfo",
]
