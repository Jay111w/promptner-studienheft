"""Demo-Modus: Entitaeten-Tab und Worker-Signal-Weg (offscreen, ohne Endpunkt)."""

import pytest

pytest.importorskip("PySide6")

from korrektor.ui.main_window import MainWindow  # noqa: E402
from korrektor.ui.widgets.entity_panel import EntityPanel  # noqa: E402
from promptner.demo import EntityHit  # noqa: E402

HITS = [
    EntityHit(pdf_page=4, text="Wolf Peter Bree", label="PER", sentence="Wolf Peter Bree kam."),
    EntityHit(pdf_page=4, text="Hildesheim", label="LOC", sentence="Er wohnt in Hildesheim."),
]


@pytest.mark.integration
def test_entity_panel_fills_table_and_summary(qtbot):
    panel = EntityPanel()
    qtbot.addWidget(panel)
    panel.set_hits(HITS)
    assert panel.table.rowCount() == 2
    assert panel.table.item(0, 0).text() == "5"  # 0-basiert -> gedruckt 1-basiert
    assert panel.table.item(0, 1).text() == "Person"
    assert panel.table.item(1, 2).text() == "Hildesheim"
    assert "2 Entitaeten" in panel._summary.text()
    panel.set_hits([])
    assert panel.table.rowCount() == 0


@pytest.mark.integration
def test_main_window_has_entity_tab_and_handles_result(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.tabs.count() == 2
    assert not window._act_entities.isEnabled()  # kein Dokument geladen
    window._on_entities_finished(HITS)
    assert window.tabs.currentWidget() is window.entity_panel
    assert window.entity_panel.table.rowCount() == 2
    assert "2 Treffer" in window._info_label.text()
