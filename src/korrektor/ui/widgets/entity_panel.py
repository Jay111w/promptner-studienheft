"""Tabelle der gefundenen Entitaeten (Demo-Modus 'Entitaeten extrahieren')."""

from __future__ import annotations

from collections import Counter

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

_LABEL_DE = {
    "PER": "Person",
    "ORG": "Organisation",
    "LOC": "Ort",
    "OTH": "Sonstiges",
    "MISC": "Sonstiges",
}


class EntityPanel(QWidget):
    """Zeigt EntityHit-Objekte als Tabelle: Seite, Typ, Text, Satz."""

    COLUMNS = ("Seite", "Typ", "Text", "Satz")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hits: list = []
        layout = QVBoxLayout(self)
        self._summary = QLabel("Noch keine Entitaeten extrahiert.")
        layout.addWidget(self._summary)
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

    def set_hits(self, hits: list) -> None:
        self.hits = list(hits)
        self.table.setRowCount(len(self.hits))
        for row, h in enumerate(self.hits):
            page = QTableWidgetItem(str(h.pdf_page + 1))
            page.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 0, page)
            self.table.setItem(row, 1, QTableWidgetItem(_LABEL_DE.get(h.label, h.label)))
            self.table.setItem(row, 2, QTableWidgetItem(h.text))
            self.table.setItem(row, 3, QTableWidgetItem(h.sentence))
        counts = Counter(h.label for h in self.hits)
        if not self.hits:
            self._summary.setText("Keine Entitaeten gefunden.")
            return
        parts = ", ".join(f"{_LABEL_DE.get(k, k)} {v}" for k, v in sorted(counts.items()))
        self._summary.setText(f"{len(self.hits)} Entitaeten: {parts}")
