"""Hauptfenster der Anwendung.

Verbindet Controller, Statusleiste, Korrektur-Panel und Hintergrund-Worker
zu einem bedienbaren Ablauf: PDF laden -> Seitenbereich waehlen -> Analyse
-> pruefen/freigeben -> exportieren.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from korrektor.config import get_logger
from korrektor.ui.view_models import AppController
from korrektor.ui.widgets.correction_panel import CorrectionPanel
from korrektor.ui.widgets.page_range_dialog import PageRangeDialog
from korrektor.ui.widgets.pdf_viewer import PdfViewer
from korrektor.ui.widgets.status_bar import StatusBar
from korrektor.ui.workers import AnalysisWorker

log = get_logger("ui.main_window")


class MainWindow(QMainWindow):
    """Das Hauptfenster des Studienheft-Korrektors."""

    def __init__(self, controller: AppController | None = None) -> None:
        super().__init__()
        self.controller = controller or AppController()
        self._thread: QThread | None = None
        self._worker: AnalysisWorker | None = None

        self.setWindowTitle("Studienheft-Korrektor")
        self.resize(1000, 640)

        self._build_toolbar()
        self._build_central()
        self._refresh_status()
        self._update_actions_enabled()

    # --- Aufbau ---
    def _build_toolbar(self) -> None:
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self._act_open = toolbar.addAction("PDF laden", self.open_pdf)
        self._act_analyze = toolbar.addAction("Analyse starten", self.start_analysis)
        self._act_export = toolbar.addAction("Exportieren", self.export_results)

    def _build_central(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        self._info_label = QLabel("Kein Dokument geladen.")
        layout.addWidget(self._info_label)

        self.viewer = PdfViewer()
        self.panel = CorrectionPanel()
        self.panel.approve_requested.connect(self._on_approve)
        self.panel.reject_requested.connect(self._on_reject)
        self.panel.edit_requested.connect(self._on_edit)
        self.panel.approve_all_requested.connect(self._on_approve_all)
        self.panel.selection_changed.connect(self._on_selection)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.viewer)
        splitter.addWidget(self.panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        layout.addWidget(splitter, stretch=1)

        self.status_widget = StatusBar()
        layout.addWidget(self.status_widget)
        self.setCentralWidget(central)

    # --- Aktionen ---
    def open_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "PDF waehlen", "", "PDF-Dateien (*.pdf)")
        if not path:
            return
        try:
            info = self.controller.load_pdf(path)
        except Exception as exc:  # noqa: BLE001
            self._show_error("PDF konnte nicht geladen werden.", str(exc))
            return
        self._info_label.setText(f"Geladen: {Path(info.path).name}  ({info.page_count} Seiten)")
        self.panel.set_corrections([])
        self.viewer.set_document(self.controller.source_path)
        self.viewer.show_page(0)
        self._refresh_status()
        self._update_actions_enabled()

    def start_analysis(self) -> None:
        if self.controller.document_info is None:
            return
        dialog = PageRangeDialog(self.controller.document_info.page_count, self)
        if not dialog.exec():
            return
        self.controller.set_page_offset(dialog.page_offset())

        self._set_busy(True)
        self._thread = QThread()
        self._worker = AnalysisWorker(self.controller, dialog.page_range())
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_analysis_finished)
        self._worker.failed.connect(self._on_analysis_failed)
        self._thread.start()
        self._refresh_status()

    def export_results(self) -> None:
        if not self.controller.corrections:
            self._show_info("Es liegen keine Korrekturen zum Export vor.")
            return
        directory = QFileDialog.getExistingDirectory(self, "Zielordner waehlen")
        if not directory:
            return
        try:
            result = self.controller.export_all(directory)
        except Exception as exc:  # noqa: BLE001
            self._show_error("Export fehlgeschlagen.", str(exc))
            self._refresh_status()
            return
        files = "\n".join(p.name for p in result.as_list())
        self._show_info(f"Export erfolgreich:\n{files}")
        self._refresh_status()

    # --- Worker-Callbacks ---
    def _on_progress(self, current: int, total: int, pdf_page: int) -> None:
        self._info_label.setText(f"Analysiere Seite {current} von {total} ...")

    def _on_analysis_finished(self, corrections: list) -> None:
        self.panel.set_corrections(corrections)
        self._info_label.setText(f"Analyse abgeschlossen: {len(corrections)} Korrektur(en).")
        self._teardown_thread()
        self._set_busy(False)
        self._refresh_status()

    def _on_analysis_failed(self, code: str, message: str) -> None:
        self._teardown_thread()
        self._set_busy(False)
        self._refresh_status()
        self._show_error(f"Analyse fehlgeschlagen ({code})", message)

    # --- Panel-Callbacks ---
    def _on_approve(self, cid: str) -> None:
        self.controller.approve(cid)
        self.panel.refresh()

    def _on_reject(self, cid: str) -> None:
        self.controller.reject(cid)
        self.panel.refresh()

    def _on_edit(self, cid: str, text: str) -> None:
        self.controller.edit(cid, text)
        self.panel.refresh()

    def _on_approve_all(self) -> None:
        self.controller.approve_all()
        self.panel.refresh()

    def _on_selection(self, cid: str) -> None:
        """Zeigt in der Vorschau die Seite der gewaehlten Korrektur."""
        for c in self.controller.corrections:
            if c.id == cid:
                rects = c.location.rects if c.location else []
                color = QColor(*c.category.rgb)  # Gelb=A, Blau=B, Gruen=C
                self.viewer.show_page(c.pdf_page, rects, color)
                break

    # --- Helfer ---
    def _teardown_thread(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
            self._worker = None

    def _set_busy(self, busy: bool) -> None:
        self._act_open.setEnabled(not busy)
        self._act_analyze.setEnabled(not busy)
        self._act_export.setEnabled(not busy)

    def _update_actions_enabled(self) -> None:
        has_doc = self.controller.document_info is not None
        self._act_analyze.setEnabled(has_doc)
        self._act_export.setEnabled(has_doc)

    def _refresh_status(self) -> None:
        self.status_widget.update_status(self.controller.status)

    def _show_error(self, title: str, detail: str) -> None:
        log.error("%s: %s", title, detail)
        QMessageBox.critical(self, title, detail)

    def _show_info(self, message: str) -> None:
        QMessageBox.information(self, "Studienheft-Korrektor", message)
