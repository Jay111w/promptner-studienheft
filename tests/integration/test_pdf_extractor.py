"""Integrationstests fuer die PDF-Extraktion gegen ein echtes PDF."""

import pytest
from tests.fixtures.pdf_factory import make_pdf

from korrektor.domain import PageRange
from korrektor.errors import ErrorCode, PdfError
from korrektor.services.pdf.extractor import PdfDocument

PAGES = [
    "Kapitel 1: Einfuehrung in die Veroeffentlichung.",
    "Kapitel 2: Die Suche nach guten Beispielen.",
    "Kapitel 3: Video und weitere Kanaele.",
]


@pytest.fixture
def sample_pdf(tmp_path):
    return make_pdf(tmp_path / "heft.pdf", PAGES)


@pytest.mark.integration
def test_open_and_count_pages(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        assert doc.page_count == 3


@pytest.mark.integration
def test_extract_single_page_text(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        text = doc.extract_page(0)
        assert "Einfuehrung" in text


@pytest.mark.integration
def test_extract_range_returns_all_pages(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        pages = doc.extract_range(PageRange(start=0, end=2))
        assert [p.pdf_page for p in pages] == [0, 1, 2]
        assert "Suche" in pages[1].text


@pytest.mark.integration
def test_search_rects_finds_quote(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        rects = doc.search_rects(2, "Video")
        assert len(rects) >= 1
        assert all(len(r) == 4 for r in rects)


@pytest.mark.integration
def test_missing_file_raises_pdf_not_found(tmp_path):
    with pytest.raises(PdfError) as excinfo:
        PdfDocument(tmp_path / "fehlt.pdf")
    assert excinfo.value.code is ErrorCode.PDF_NOT_FOUND


@pytest.mark.integration
def test_page_out_of_range_raises(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        with pytest.raises(PdfError) as excinfo:
            doc.extract_page(99)
        assert excinfo.value.code is ErrorCode.PDF_PAGE_OUT_OF_RANGE


@pytest.mark.integration
def test_paragraph_label_for_match(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        rects = doc.search_rects(0, "Einfuehrung")
        label = doc.paragraph_label(0, rects)
    assert label.startswith("Absatz")


@pytest.mark.integration
def test_paragraph_label_empty_without_rects(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        assert doc.paragraph_label(0, []) == ""


@pytest.mark.integration
def test_build_document_info_with_offset(sample_pdf):
    with PdfDocument(sample_pdf) as doc:
        info = doc.build_document_info(page_offset=-2)
        assert info.page_count == 3
        assert info.page_mapping.to_printed(2) == 1
