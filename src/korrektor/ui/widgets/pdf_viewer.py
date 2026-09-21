"""Einfache PDF-Seitenvorschau mit optionaler Trefferhervorhebung.

Rendert eine Seite via PyMuPDF zu einem Bild und zeichnet die Rechtecke der
ausgewaehlten Korrektur als halbtransparente Hervorhebung darueber.
"""

from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea

from korrektor.config import get_logger

log = get_logger("ui.pdf_viewer")

Rect = tuple[float, float, float, float]
_ZOOM = 1.5  # Render-Vergroesserung


class PdfViewer(QScrollArea):
    """Zeigt eine einzelne PDF-Seite als Bild an."""

    def __init__(self) -> None:
        super().__init__()
        self._label = QLabel("Keine Vorschau.")
        self._label.setAlignment(Qt.AlignCenter)
        self.setWidget(self._label)
        self.setWidgetResizable(True)
        self._path: Path | None = None

    def set_document(self, path: str | Path | None) -> None:
        """Legt das anzuzeigende PDF fest (oder leert die Vorschau)."""
        self._path = Path(path) if path else None
        if self._path is None:
            self._label.setText("Keine Vorschau.")

    def show_page(
        self,
        page_index: int,
        highlights: list[Rect] | None = None,
        color: QColor | None = None,
    ) -> None:
        """Rendert eine Seite und hebt optional Trefferrechtecke hervor.

        Args:
            page_index: 0-basierter PDF-Seitenindex.
            highlights: Rechtecke der hervorzuhebenden Stelle.
            color: Farbe der Hervorhebung (Standard: halbtransparentes Gelb).
        """
        if self._path is None:
            return
        try:
            pixmap = self._render(page_index, highlights or [], color)
        except Exception as exc:  # noqa: BLE001 - Vorschau darf nie crashen
            log.warning("Vorschau fehlgeschlagen (Seite %d): %s", page_index, exc)
            self._label.setText("Vorschau nicht verfuegbar.")
            return
        self._label.setPixmap(pixmap)

    def _render(self, page_index: int, highlights: list[Rect], color: QColor | None) -> QPixmap:
        with fitz.open(self._path) as doc:
            page = doc[page_index]
            matrix = fitz.Matrix(_ZOOM, _ZOOM)
            pix = page.get_pixmap(matrix=matrix)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image.copy())

        if highlights:
            self._draw_highlights(pixmap, highlights, color)
        return pixmap

    @staticmethod
    def _draw_highlights(pixmap: QPixmap, highlights: list[Rect], color: QColor | None) -> None:
        fill = QColor(color) if color is not None else QColor(255, 214, 0)
        fill.setAlpha(90)  # halbtransparent
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(fill)
        for x0, y0, x1, y1 in highlights:
            painter.drawRect(
                int(x0 * _ZOOM),
                int(y0 * _ZOOM),
                int((x1 - x0) * _ZOOM),
                int((y1 - y0) * _ZOOM),
            )
        painter.end()
