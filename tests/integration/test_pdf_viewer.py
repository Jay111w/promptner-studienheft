"""Smoke-Tests fuer die PDF-Vorschau (headless)."""

import pytest

pytest.importorskip("PySide6")

from tests.fixtures.pdf_factory import make_pdf  # noqa: E402

from korrektor.ui.widgets.pdf_viewer import PdfViewer  # noqa: E402


@pytest.fixture
def pdf(tmp_path):
    return make_pdf(tmp_path / "heft.pdf", ["Seite eins.", "Seite zwei."])


@pytest.mark.integration
def test_viewer_shows_page(qtbot, pdf):
    viewer = PdfViewer()
    qtbot.addWidget(viewer)
    viewer.set_document(pdf)
    viewer.show_page(0)
    assert viewer._label.pixmap() is not None
    assert not viewer._label.pixmap().isNull()


@pytest.mark.integration
def test_viewer_with_highlights_does_not_crash(qtbot, pdf):
    viewer = PdfViewer()
    qtbot.addWidget(viewer)
    viewer.set_document(pdf)
    viewer.show_page(0, highlights=[(72.0, 72.0, 120.0, 84.0)])
    assert not viewer._label.pixmap().isNull()


@pytest.mark.integration
def test_viewer_without_document_is_safe(qtbot):
    viewer = PdfViewer()
    qtbot.addWidget(viewer)
    viewer.set_document(None)
    viewer.show_page(0)  # darf nicht crashen
    assert viewer._label.text() == "Keine Vorschau."
