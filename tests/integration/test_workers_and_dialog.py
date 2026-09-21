"""Tests fuer den Analyse-Worker und den Seitenbereichs-Dialog."""

import pytest

pytest.importorskip("PySide6")

from korrektor.domain import (  # noqa: E402
    ActionType,
    Category,
    Correction,
    PageRange,
)
from korrektor.errors import ErrorCode  # noqa: E402
from korrektor.services.pdf.page_mapper import detect_offset  # noqa: E402
from korrektor.ui.view_models import AppController  # noqa: E402
from korrektor.ui.widgets.page_range_dialog import PageRangeDialog  # noqa: E402
from korrektor.ui.workers import AnalysisWorker  # noqa: E402


def _correction() -> Correction:
    return Correction(
        id="K-001",
        pdf_page=0,
        original_text="x",
        corrected_text="y",
        category=Category.A,
        action_type=ActionType.REPLACE,
    )


@pytest.mark.integration
def test_worker_emits_finished(qtbot):
    ctrl = AppController()
    # run_analysis durch eine deterministische Variante ersetzen.
    ctrl.run_analysis = lambda pr, on_progress=None: [_correction()]
    worker = AnalysisWorker(ctrl, PageRange(start=0, end=0))
    with qtbot.waitSignal(worker.finished, timeout=1000) as blocker:
        worker.run()
    assert len(blocker.args[0]) == 1


@pytest.mark.integration
def test_worker_emits_failed_without_document(qtbot):
    ctrl = AppController()  # kein Dokument geladen
    worker = AnalysisWorker(ctrl, PageRange(start=0, end=0))
    with qtbot.waitSignal(worker.failed, timeout=1000) as blocker:
        worker.run()
    assert blocker.args[0] == ErrorCode.INVALID_INPUT.value


@pytest.mark.integration
def test_page_range_dialog_returns_zero_based_range_and_offset(qtbot):
    dialog = PageRangeDialog(page_count=10)
    qtbot.addWidget(dialog)
    dialog._start.setValue(3)
    dialog._end.setValue(5)
    dialog._ref_pdf.setValue(3)
    dialog._ref_printed.setValue(1)

    pr = dialog.page_range()
    assert pr.start == 2 and pr.end == 4
    # Heft-Seite 1 auf PDF-Index 2 -> Offset -2.
    assert dialog.page_offset() == detect_offset(2, 1) == -2


@pytest.mark.integration
def test_page_range_dialog_swaps_reversed_bounds(qtbot):
    dialog = PageRangeDialog(page_count=10)
    qtbot.addWidget(dialog)
    dialog._start.setValue(8)
    dialog._end.setValue(4)
    dialog._on_accept()
    pr = dialog.page_range()
    assert pr.start <= pr.end
