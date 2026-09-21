"""Unit-Tests fuer den OCR-Trennungsfilter."""

import pytest

from korrektor.domain import ActionType, Category, Correction
from korrektor.services.analysis.ocr_filter import (
    filter_ocr_artifacts,
    is_ocr_hyphenation_only,
)


def _correction(original: str, corrected: str, action=ActionType.REPLACE) -> Correction:
    return Correction(
        id="K-001",
        pdf_page=0,
        original_text=original,
        corrected_text=corrected,
        category=Category.A,
        action_type=action,
    )


@pytest.mark.unit
def test_pure_hyphenation_is_detected():
    c = _correction("Veroeffentlichungs-kanaele", "Veroeffentlichungskanaele")
    assert is_ocr_hyphenation_only(c) is True


@pytest.mark.unit
def test_real_spelling_fix_is_kept():
    c = _correction("Veranstalltung", "Veranstaltung")
    assert is_ocr_hyphenation_only(c) is False


@pytest.mark.unit
def test_non_replace_action_is_not_hyphenation():
    c = _correction("Wort", "", action=ActionType.DELETE)
    assert is_ocr_hyphenation_only(c) is False


@pytest.mark.unit
def test_filter_removes_only_artifacts():
    artifact = _correction("Su-che", "Suche")
    real = _correction("Veranstalltung", "Veranstaltung")
    kept = filter_ocr_artifacts([artifact, real])
    assert kept == [real]
