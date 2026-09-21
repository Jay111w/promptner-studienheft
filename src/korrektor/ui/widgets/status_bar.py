"""Statusleiste mit den vier Indikatoren der Anwendung.

Zeigt jederzeit: App laeuft, OpenAI verbunden, Analyse aktiv, Fehler.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from korrektor.ui.view_models import AppStatus

_OK = "#2e7d32"  # gruen
_OFF = "#9e9e9e"  # grau
_ACTIVE = "#1565c0"  # blau
_ERROR = "#c62828"  # rot


class _Indicator(QWidget):
    """Ein einzelner Punkt-Indikator mit Beschriftung."""

    def __init__(self, caption: str) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        self._dot = QLabel("●")  # gefuellter Kreis
        self._text = QLabel(caption)
        layout.addWidget(self._dot)
        layout.addWidget(self._text)
        self.set_color(_OFF)

    def set_color(self, color: str) -> None:
        self._dot.setStyleSheet(f"color: {color}; font-size: 14px;")


class StatusBar(QWidget):
    """Leiste mit den vier Statusindikatoren."""

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        self._app = _Indicator("App")
        self._api = _Indicator("OpenAI")
        self._analysis = _Indicator("Analyse")
        self._error = _Indicator("Fehler")
        for w in (self._app, self._api, self._analysis, self._error):
            layout.addWidget(w)
        layout.addStretch(1)

    def update_status(self, status: AppStatus) -> None:
        """Faerbt die Indikatoren entsprechend dem aktuellen Status."""
        self._app.set_color(_OK if status.app_running else _OFF)
        self._api.set_color(_OK if status.api_configured else _OFF)
        self._analysis.set_color(_ACTIVE if status.analysis_active else _OFF)
        self._error.set_color(_ERROR if status.has_errors else _OFF)
