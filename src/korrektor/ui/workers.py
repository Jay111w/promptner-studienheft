"""Hintergrund-Worker fuer die Analyse.

Laeuft in einem eigenen QThread, damit die Oberflaeche waehrend der
KI-Verarbeitung reaktionsfaehig bleibt. Kommuniziert ausschliesslich ueber
Signale.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from korrektor.config import get_logger
from korrektor.domain import PageRange
from korrektor.errors import ErrorCode, KorrektorError
from korrektor.ui.view_models import AppController

log = get_logger("ui.workers")


class AnalysisWorker(QObject):
    """Fuehrt :meth:`AppController.run_analysis` in einem Thread aus."""

    progress = Signal(int, int, int)  # (aktuell, gesamt, pdf_page)
    finished = Signal(list)  # list[Correction]
    failed = Signal(str, str)  # (fehlercode, meldung)

    def __init__(self, controller: AppController, page_range: PageRange) -> None:
        super().__init__()
        self._controller = controller
        self._page_range = page_range

    @Slot()
    def run(self) -> None:
        try:
            results = self._controller.run_analysis(
                self._page_range, on_progress=self.progress.emit
            )
            self.finished.emit(results)
        except KorrektorError as exc:
            log.error("Analyse fehlgeschlagen: %s", exc.code.value)
            self.failed.emit(exc.code.value, exc.message)
        except Exception as exc:  # noqa: BLE001 - letzte Auffanglinie
            log.exception("Unerwarteter Fehler in der Analyse.")
            self.failed.emit(ErrorCode.UNKNOWN.value, str(exc))


class EntityWorker(QObject):
    """Extrahiert Entitaeten (PromptNER-Demo) aus einem PDF-Seitenbereich in einem Thread."""

    progress = Signal(int, int)  # (Saetze fertig, Saetze gesamt)
    finished = Signal(list)  # list[EntityHit]
    failed = Signal(str, str)  # (fehlercode, meldung)

    def __init__(self, pdf_path: str, page_range: PageRange) -> None:
        super().__init__()
        self._pdf_path = pdf_path
        self._page_range = page_range

    @Slot()
    def run(self) -> None:
        try:
            from pathlib import Path

            from promptner.config.settings import get_settings
            from promptner.demo import extract_from_pdf
            from promptner.llm.cache import ResponseCache
            from promptner.llm.client import LlmClient

            s = get_settings()
            cache = ResponseCache(Path(s.cache_dir))
            try:
                hits = extract_from_pdf(
                    self._pdf_path,
                    LlmClient(settings=s),
                    first_page=self._page_range.start,
                    last_page=self._page_range.end,
                    model=s.llm_model,
                    cache=cache,
                    on_progress=self.progress.emit,
                )
            finally:
                cache.close()
            self.finished.emit(hits)
        except Exception as exc:  # noqa: BLE001 - letzte Auffanglinie
            code = getattr(getattr(exc, "code", None), "value", ErrorCode.UNKNOWN.value)
            log.exception("Entitaeten-Extraktion fehlgeschlagen.")
            self.failed.emit(str(code), getattr(exc, "message", str(exc)))
