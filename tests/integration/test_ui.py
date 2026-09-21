"""UI-Smoke-Tests mit pytest-qt (headless / offscreen)."""

import pytest

pytest.importorskip("PySide6")

from korrektor.domain import (  # noqa: E402
    ActionType,
    Category,
    Correction,
    CorrectionStatus,
)
from korrektor.ui.view_models import AppController, AppStatus  # noqa: E402
from korrektor.ui.widgets.correction_panel import CorrectionPanel  # noqa: E402
from korrektor.ui.widgets.status_bar import StatusBar  # noqa: E402


def _correction(cid: str = "K-001") -> Correction:
    return Correction(
        id=cid,
        pdf_page=0,
        printed_page=1,
        original_text="Veranstalltung",
        corrected_text="Veranstaltung",
        category=Category.A,
        action_type=ActionType.REPLACE,
    )


@pytest.mark.integration
def test_status_bar_reflects_state(qtbot):
    bar = StatusBar()
    qtbot.addWidget(bar)
    bar.update_status(AppStatus(api_configured=True, has_errors=True))
    # OpenAI-Indikator gruen, Fehler-Indikator rot.
    assert "#2e7d32" in bar._api._dot.styleSheet()
    assert "#c62828" in bar._error._dot.styleSheet()


@pytest.mark.integration
def test_correction_panel_populates_and_selects(qtbot):
    panel = CorrectionPanel()
    qtbot.addWidget(panel)
    panel.set_corrections([_correction("K-001"), _correction("K-002")])
    assert panel._table.rowCount() == 2
    assert panel.selected_id() == "K-001"


@pytest.mark.integration
def test_correction_panel_emits_approve(qtbot):
    panel = CorrectionPanel()
    qtbot.addWidget(panel)
    panel.set_corrections([_correction("K-001")])
    with qtbot.waitSignal(panel.approve_requested, timeout=1000) as blocker:
        panel._btn_approve.click()
    assert blocker.args == ["K-001"]


@pytest.mark.integration
def test_main_window_wires_panel_to_controller(qtbot):
    from korrektor.ui.main_window import MainWindow

    controller = AppController()
    controller.corrections = [_correction("K-001")]
    window = MainWindow(controller)
    qtbot.addWidget(window)

    window.panel.set_corrections(controller.corrections)
    # Freigabe ueber das Panel-Signal landet im Controller.
    window.panel.approve_requested.emit("K-001")
    assert controller.corrections[0].status is CorrectionStatus.APPROVED

    window.panel.approve_all_requested.emit()
    assert controller.corrections[0].status is CorrectionStatus.APPROVED
