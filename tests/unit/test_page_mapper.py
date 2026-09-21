"""Unit-Tests fuer das Seiten-Mapping (PDF <-> gedruckte Heft-Seite)."""

import pytest

from korrektor.services.pdf.page_mapper import PageMapper, detect_offset


@pytest.mark.unit
def test_detect_offset_with_cover_page():
    # Heft-Seite 1 steht auf PDF-Index 2 (3. Seite) -> Offset -2
    assert detect_offset(pdf_page_index=2, printed_page_number=1) == -2


@pytest.mark.unit
def test_detect_offset_identity():
    # Heft-Seite 1 auf PDF-Index 0 -> Offset 0
    assert detect_offset(pdf_page_index=0, printed_page_number=1) == 0


@pytest.mark.unit
def test_mapper_from_reference_maps_correctly():
    mapper = PageMapper.from_reference(pdf_page_index=2, printed_page_number=1)
    assert mapper.printed_page(2) == 1
    assert mapper.printed_page(3) == 2


@pytest.mark.unit
def test_mapper_label_shows_both_pages():
    mapper = PageMapper.from_reference(pdf_page_index=2, printed_page_number=1)
    label = mapper.label(3)
    assert "PDF-Seite 4" in label
    assert "Heft-Seite 2" in label
