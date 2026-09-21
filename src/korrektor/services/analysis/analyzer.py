"""Orchestriert die kapitelweise Korrektur-Analyse.

Verbindet PDF-Extraktion, KI-Aufruf, Antwort-Parsing und OCR-Filter zu einem
Ablauf: Seitenbereich rein -> Liste von :class:`Correction` raus. Vergibt
fortlaufende, dokumentweit eindeutige IDs und lokalisiert jede Korrektur fuer
die spaetere PDF-Annotation.
"""

from __future__ import annotations

from collections.abc import Callable

from korrektor.config import get_logger, get_settings
from korrektor.domain import Correction, PageRange, make_correction_id
from korrektor.errors import AiError, ErrorCode
from korrektor.services.ai.openai_client import OpenAiClient
from korrektor.services.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from korrektor.services.ai.response_parser import parse_corrections
from korrektor.services.analysis.ocr_filter import filter_ocr_artifacts
from korrektor.services.pdf.extractor import PdfDocument
from korrektor.services.pdf.page_mapper import PageMapper

log = get_logger("services.analysis.analyzer")

# Callback fuer Fortschrittsmeldungen ans UI: (aktuell, gesamt, pdf_page).
ProgressCallback = Callable[[int, int, int], None]


class Analyzer:
    """Fuehrt die Korrektur-Analyse ueber einen Seitenbereich aus."""

    def __init__(
        self,
        client: OpenAiClient | None = None,
        mapper: PageMapper | None = None,
        max_chars_per_segment: int | None = None,
    ) -> None:
        self._client = client or OpenAiClient()
        self._mapper = mapper or PageMapper()
        self._max_chars = max_chars_per_segment or get_settings().max_chars_per_segment

    def analyze_range(
        self,
        document: PdfDocument,
        page_range: PageRange,
        on_progress: ProgressCallback | None = None,
    ) -> list[Correction]:
        """Analysiert alle Seiten eines Bereichs und liefert die Korrekturen.

        Raises:
            AiError: Wenn ein Segment das Zeichenlimit ueberschreitet oder die
                KI-Verarbeitung fehlschlaegt.
        """
        pages = document.extract_range(page_range)
        results: list[Correction] = []

        for position, page in enumerate(pages, start=1):
            if len(page.text) > self._max_chars:
                raise AiError(
                    ErrorCode.SEGMENT_TOO_LARGE,
                    context={
                        "pdf_page": page.pdf_page,
                        "chars": len(page.text),
                        "limit": self._max_chars,
                    },
                )

            printed = self._mapper.printed_page(page.pdf_page)
            raw = self._client.complete_json(SYSTEM_PROMPT, build_user_prompt(page.text, printed))
            # Provisorische IDs; final wird dokumentweit nach dem Filtern vergeben.
            corrections = parse_corrections(
                raw,
                pdf_page=page.pdf_page,
                printed_page=printed,
            )
            corrections = filter_ocr_artifacts(corrections)
            self._locate(document, corrections)

            results.extend(corrections)
            if on_progress is not None:
                on_progress(position, len(pages), page.pdf_page)

        # Dokumentweit eindeutige, lueckenlose IDs vergeben (z. B. K-001, K-002).
        for i, correction in enumerate(results, start=1):
            correction.id = make_correction_id(i)

        log.info(
            "Analyse abgeschlossen: %d Korrektur(en) auf %d Seite(n).",
            len(results),
            len(pages),
        )
        return results

    @staticmethod
    def _locate(document: PdfDocument, corrections: list[Correction]) -> None:
        """Ergaenzt Trefferkoordinaten fuer die spaetere Annotation."""
        for c in corrections:
            if c.location is None or not c.location.quote:
                continue
            rects = document.search_rects(c.pdf_page, c.location.quote)
            c.location.rects = rects
            if rects and not c.paragraph:
                c.paragraph = document.paragraph_label(c.pdf_page, rects)
