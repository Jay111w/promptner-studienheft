"""Anwendungs-Controller (GUI-unabhaengig).

Bindeglied zwischen Oberflaeche und Services. Bewusst ohne Qt-Abhaengigkeit,
damit der gesamte Ablauf (Laden, Analyse, Freigabe, Export) ohne GUI testbar
bleibt. Die Qt-Schicht ruft nur diese Methoden auf und spiegelt den Status.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from korrektor.config import get_logger, get_settings
from korrektor.config.settings import Settings
from korrektor.domain import (
    Correction,
    CorrectionStatus,
    DocumentInfo,
    PageMapping,
    PageRange,
)
from korrektor.errors import ErrorCode, KorrektorError
from korrektor.services.analysis.analyzer import Analyzer
from korrektor.services.export import (
    export_annotated_pdf,
    export_changelog,
    export_word,
)
from korrektor.services.pdf.extractor import PdfDocument
from korrektor.services.pdf.page_mapper import PageMapper

log = get_logger("ui.controller")


@dataclass
class AppStatus:
    """Die vier sichtbaren Statusindikatoren der Anwendung."""

    app_running: bool = True
    api_configured: bool = False
    analysis_active: bool = False
    has_errors: bool = False
    last_error: str = ""

    def as_dict(self) -> dict[str, bool]:
        return {
            "app_running": self.app_running,
            "api_configured": self.api_configured,
            "analysis_active": self.analysis_active,
            "has_errors": self.has_errors,
        }


@dataclass
class ExportResult:
    """Pfade der drei erzeugten Ausgabedateien."""

    annotated_pdf: Path
    word: Path
    changelog_pdf: Path

    def as_list(self) -> list[Path]:
        return [self.annotated_pdf, self.word, self.changelog_pdf]


class AppController:
    """Kapselt Zustand und Ablaeufe der Anwendung."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.status = AppStatus(api_configured=self.settings.has_api_key)
        self.document_info: DocumentInfo | None = None
        self.corrections: list[Correction] = []
        self._source_path: Path | None = None

    @property
    def source_path(self) -> Path | None:
        """Pfad des aktuell geladenen PDFs (oder None)."""
        return self._source_path

    # --- Dokument ---
    def load_pdf(self, path: str | Path, page_offset: int = 0) -> DocumentInfo:
        """Laedt ein PDF und merkt sich dessen Metadaten."""
        with PdfDocument(path) as doc:
            info = doc.build_document_info(page_offset=page_offset)
        self._source_path = Path(path)
        self.document_info = info
        self.corrections = []
        self._clear_error()
        log.info("Dokument geladen: %s (%d Seiten).", info.path, info.page_count)
        return info

    def set_page_offset(self, offset: int) -> None:
        """Aktualisiert den Seiten-Offset (PDF -> gedruckte Heft-Seite)."""
        if self.document_info is None:
            raise KorrektorError(ErrorCode.INVALID_INPUT, "Kein Dokument geladen.")
        self.document_info.page_mapping = PageMapping(offset=offset)

    # --- Analyse ---
    def run_analysis(
        self,
        page_range: PageRange,
        analyzer: Analyzer | None = None,
        on_progress=None,
    ) -> list[Correction]:
        """Analysiert einen Seitenbereich und speichert die Korrekturen.

        Raises:
            KorrektorError: Wenn kein Dokument geladen ist oder die Analyse
                fehlschlaegt (Status ``has_errors`` wird gesetzt).
        """
        if self.document_info is None or self._source_path is None:
            raise KorrektorError(ErrorCode.INVALID_INPUT, "Kein Dokument geladen.")

        self.status.analysis_active = True
        self._clear_error()
        try:
            engine = analyzer or Analyzer(mapper=PageMapper(self.document_info.page_mapping))
            with PdfDocument(self._source_path) as doc:
                results = engine.analyze_range(doc, page_range, on_progress)
            self.corrections = results
            return results
        except KorrektorError as exc:
            self._set_error(exc.message)
            raise
        finally:
            self.status.analysis_active = False

    # --- Freigabe-Workflow ---
    def _find(self, correction_id: str) -> Correction:
        for c in self.corrections:
            if c.id == correction_id:
                return c
        raise KorrektorError(ErrorCode.INVALID_INPUT, f"Unbekannte Korrektur: {correction_id}")

    def approve(self, correction_id: str) -> None:
        self._find(correction_id).status = CorrectionStatus.APPROVED

    def reject(self, correction_id: str) -> None:
        self._find(correction_id).status = CorrectionStatus.REJECTED

    def edit(self, correction_id: str, corrected_text: str) -> None:
        """Bearbeitet den Korrekturtext und markiert die Korrektur als bearbeitet."""
        c = self._find(correction_id)
        c.corrected_text = corrected_text
        c.status = CorrectionStatus.EDITED

    def approve_all(self) -> None:
        """'Alle uebernehmen': alle noch offenen Vorschlaege freigeben."""
        for c in self.corrections:
            if c.status is CorrectionStatus.PROPOSED:
                c.status = CorrectionStatus.APPROVED

    def accepted_corrections(self) -> list[Correction]:
        """Korrekturen, die exportiert werden (freigegeben oder bearbeitet)."""
        accepted = {CorrectionStatus.APPROVED, CorrectionStatus.EDITED}
        return [c for c in self.corrections if c.status in accepted]

    # --- Export ---
    def export_all(self, output_dir: str | Path) -> ExportResult:
        """Erzeugt annotiertes PDF, Word-Tabelle und Changelog-PDF.

        Es werden nur freigegebene/bearbeitete Korrekturen exportiert.

        Raises:
            KorrektorError: Wenn kein Dokument geladen ist oder ein Export
                fehlschlaegt.
        """
        if self._source_path is None:
            raise KorrektorError(ErrorCode.INVALID_INPUT, "Kein Dokument geladen.")

        output_dir = Path(output_dir)
        stem = self._source_path.stem
        items = self.accepted_corrections()
        try:
            result = ExportResult(
                annotated_pdf=export_annotated_pdf(
                    self._source_path, items, output_dir / f"{stem}_korrigiert.pdf"
                ),
                word=export_word(items, output_dir / f"{stem}_korrekturen.docx"),
                changelog_pdf=export_changelog(
                    items, output_dir / f"{stem}_aenderungen.pdf", document_name=stem
                ),
            )
        except KorrektorError as exc:
            self._set_error(exc.message)
            raise
        log.info("Export abgeschlossen: %d Korrekturen.", len(items))
        return result

    # --- Status-Helfer ---
    def _set_error(self, message: str) -> None:
        self.status.has_errors = True
        self.status.last_error = message

    def _clear_error(self) -> None:
        self.status.has_errors = False
        self.status.last_error = ""
