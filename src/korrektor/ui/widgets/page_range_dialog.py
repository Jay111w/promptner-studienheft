"""Dialog zur Auswahl eines Seitenbereichs (Kapitel) und des Seiten-Offsets.

Der Nutzer waehlt die zu pruefenden Seiten (1-basiert, wie im Heft sichtbar)
und kann ueber einen Referenzpunkt festlegen, welche gedruckte Heft-Seitenzahl
einer PDF-Seite entspricht.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QVBoxLayout,
)

from korrektor.domain import PageRange
from korrektor.services.pdf.page_mapper import detect_offset


class PageRangeDialog(QDialog):
    """Fragt Seitenbereich (0-basiert intern) und Seiten-Offset ab."""

    def __init__(self, page_count: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Seitenbereich waehlen")
        self._page_count = page_count

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._start = QSpinBox()
        self._start.setRange(1, page_count)
        self._start.setValue(1)
        self._end = QSpinBox()
        self._end.setRange(1, page_count)
        self._end.setValue(page_count)
        form.addRow("Von PDF-Seite:", self._start)
        form.addRow("Bis PDF-Seite:", self._end)
        layout.addLayout(form)

        # Optionaler Referenzpunkt fuer die gedruckte Heft-Seitenzahl.
        ref_box = QGroupBox("Heft-Seitenzahl zuordnen (optional)")
        ref_form = QFormLayout(ref_box)
        self._ref_pdf = QSpinBox()
        self._ref_pdf.setRange(1, page_count)
        self._ref_pdf.setValue(1)
        self._ref_printed = QSpinBox()
        self._ref_printed.setRange(1, 9999)
        self._ref_printed.setValue(1)
        ref_form.addRow("Auf PDF-Seite:", self._ref_pdf)
        ref_form.addRow("steht Heft-Seite:", self._ref_printed)
        layout.addWidget(ref_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if self._end.value() < self._start.value():
            # Werte tauschen, statt den Nutzer zu blockieren.
            self._start.setValue(self._end.value())
        self.accept()

    def page_range(self) -> PageRange:
        """Gewaehlter Bereich, intern 0-basiert."""
        return PageRange(start=self._start.value() - 1, end=self._end.value() - 1)

    def page_offset(self) -> int:
        """Offset aus dem Referenzpunkt (PDF-Seite -> gedruckte Heft-Seite)."""
        return detect_offset(
            pdf_page_index=self._ref_pdf.value() - 1,
            printed_page_number=self._ref_printed.value(),
        )
