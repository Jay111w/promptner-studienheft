"""Unit-Tests fuer die Domain-Modelle."""

import pytest

from korrektor.domain import (
    ActionType,
    Category,
    Correction,
    CorrectionStatus,
    PageMapping,
    PageRange,
    make_correction_id,
)


@pytest.mark.unit
def test_make_correction_id_is_zero_padded():
    assert make_correction_id(1) == "K-001"
    assert make_correction_id(42) == "K-042"


@pytest.mark.unit
def test_category_label():
    assert Category.A.label == "Sicherer Fehler"
    assert Category.C.label == "Stil-/Redaktionsentscheidung"


@pytest.mark.unit
def test_category_colors_yellow_blue_green():
    # Gelb = A, Blau = B, Gruen = C
    assert Category.A.rgb == (255, 214, 0)
    assert Category.B.rgb == (33, 150, 243)
    assert Category.C.rgb == (76, 175, 80)


@pytest.mark.unit
def test_page_range_pages_inclusive():
    pr = PageRange(start=2, end=4)
    assert list(pr.pages()) == [2, 3, 4]
    assert len(pr) == 3


@pytest.mark.unit
def test_page_range_rejects_reversed_bounds():
    with pytest.raises(ValueError):
        PageRange(start=5, end=2)


@pytest.mark.unit
def test_page_mapping_offset():
    # Heft-Seite 1 beginnt auf PDF-Seite 3 (Index 2): offset = -2
    mapping = PageMapping(offset=-2)
    assert mapping.to_printed(2) == 1  # pdf_page 2 -> 2 + 1 + (-2) = 1


@pytest.mark.unit
def test_correction_comment_contains_all_parts():
    c = Correction(
        id=make_correction_id(1),
        pdf_page=0,
        printed_page=1,
        original_text="diese Veranstalltung",
        corrected_text="diese Veranstaltung",
        category=Category.A,
        action_type=ActionType.REPLACE,
        description="Doppel-l",
        reason="Rechtschreibung (Duden)",
    )
    text = c.comment_text()
    assert "[K-001]" in text
    assert "Kategorie A" in text
    assert "ersetzen durch" in text
    assert "diese Veranstaltung" in text
    assert c.status is CorrectionStatus.PROPOSED
