"""Korrektur-Panel: Vorschlaege pruefen, freigeben, verwerfen, bearbeiten.

Setzt den Workflow 'pruefen & freigeben' um und bietet zusaetzlich
'Alle uebernehmen'. Aenderungen werden als Signale gemeldet; die eigentliche
Zustandsaenderung uebernimmt der Controller.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from korrektor.domain import Correction

_COLUMNS = ["ID", "Kat.", "Heft-S.", "Original", "Korrektur", "Status"]


class CorrectionPanel(QWidget):
    """Tabellarische Anzeige und Bearbeitung der Korrekturvorschlaege."""

    approve_requested = Signal(str)
    reject_requested = Signal(str)
    edit_requested = Signal(str, str)
    approve_all_requested = Signal()
    selection_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._corrections: list[Correction] = []

        layout = QVBoxLayout(self)
        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self._table)

        buttons = QHBoxLayout()
        self._btn_approve = QPushButton("Freigeben")
        self._btn_reject = QPushButton("Verwerfen")
        self._btn_edit = QPushButton("Bearbeiten")
        self._btn_all = QPushButton("Alle uebernehmen")
        for b in (self._btn_approve, self._btn_reject, self._btn_edit):
            buttons.addWidget(b)
        buttons.addStretch(1)
        buttons.addWidget(self._btn_all)
        layout.addLayout(buttons)

        self._btn_approve.clicked.connect(self._on_approve)
        self._btn_reject.clicked.connect(self._on_reject)
        self._btn_edit.clicked.connect(self._on_edit)
        self._btn_all.clicked.connect(self.approve_all_requested.emit)
        self._table.itemSelectionChanged.connect(self._on_selection)

    # --- Befuellen ---
    def set_corrections(self, corrections: list[Correction]) -> None:
        """Zeigt die uebergebenen Korrekturen an."""
        self._corrections = list(corrections)
        self._table.setRowCount(len(self._corrections))
        for row, c in enumerate(self._corrections):
            self._set_row(row, c)
        if self._corrections:
            self._table.selectRow(0)

    def refresh(self) -> None:
        """Aktualisiert die Anzeige (z. B. Status-/Textaenderungen)."""
        for row, c in enumerate(self._corrections):
            self._set_row(row, c)

    def _set_row(self, row: int, c: Correction) -> None:
        printed = str(c.printed_page) if c.printed_page is not None else "-"
        values = [
            c.id,
            c.category.value,
            printed,
            c.original_text,
            c.corrected_text or "-",
            c.status.value,
        ]
        for col, value in enumerate(values):
            self._table.setItem(row, col, QTableWidgetItem(value))

    # --- Auswahl ---
    def selected_id(self) -> str | None:
        row = self._table.currentRow()
        if 0 <= row < len(self._corrections):
            return self._corrections[row].id
        return None

    def _selected(self) -> Correction | None:
        row = self._table.currentRow()
        if 0 <= row < len(self._corrections):
            return self._corrections[row]
        return None

    # --- Aktionen ---
    def _on_approve(self) -> None:
        cid = self.selected_id()
        if cid is not None:
            self.approve_requested.emit(cid)

    def _on_reject(self) -> None:
        cid = self.selected_id()
        if cid is not None:
            self.reject_requested.emit(cid)

    def _on_selection(self) -> None:
        cid = self.selected_id()
        if cid is not None:
            self.selection_changed.emit(cid)

    def _on_edit(self) -> None:
        current = self._selected()
        if current is None:
            return
        text, ok = QInputDialog.getText(
            self,
            "Korrektur bearbeiten",
            f"Korrigierter Text fuer {current.id}:",
            text=current.corrected_text,
        )
        if ok:
            self.edit_requested.emit(current.id, text)
