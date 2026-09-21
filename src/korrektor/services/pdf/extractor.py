"""PDF-Extraktion auf Basis von PyMuPDF (``fitz``).

Stellt Text und Trefferkoordinaten je Seite bereit. Die Koordinaten werden
spaeter fuer native PDF-Annotationen (Highlights/Kommentare) verwendet.

Hinweis zur OCR-Regel: Diese Schicht liefert den Text *roh* (inkl. evtl.
durch den PDF-Export entstandener Worttrennungen). Ob solche Trennungen als
Fehler gelten, entscheidet erst die Analyse-Schicht.
"""

from __future__ import annotations

from pathlib import Path
from types import TracebackType

import fitz  # PyMuPDF

from korrektor.config import get_logger
from korrektor.domain import DocumentInfo, PageMapping, PageRange
from korrektor.errors import ErrorCode, PdfError

log = get_logger("services.pdf.extractor")

# Ein Rechteck (x0, y0, x1, y1) in PDF-Koordinaten.
Rect = tuple[float, float, float, float]


class PageText:
    """Extrahierter Text einer einzelnen PDF-Seite."""

    def __init__(self, pdf_page: int, text: str) -> None:
        self.pdf_page = pdf_page
        self.text = text

    def __repr__(self) -> str:  # pragma: no cover - reine Diagnose
        return f"PageText(pdf_page={self.pdf_page}, chars={len(self.text)})"


class PdfDocument:
    """Geoeffnetes PDF-Dokument mit Extraktions- und Suchfunktionen.

    Als Kontextmanager nutzbar::

        with PdfDocument("heft.pdf") as doc:
            text = doc.extract_page(0)
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.is_file():
            raise PdfError(
                ErrorCode.PDF_NOT_FOUND,
                context={"path": str(self.path)},
            )
        try:
            self._doc = fitz.open(self.path)
        except Exception as exc:  # noqa: BLE001 - in PdfError uebersetzen
            raise PdfError(
                ErrorCode.PDF_READ_FAILED,
                context={"path": str(self.path)},
                cause=exc,
            ) from exc
        log.info("PDF geoeffnet: %s (%d Seiten)", self.path.name, self.page_count)

    # --- Kontextmanager ---
    def __enter__(self) -> PdfDocument:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        if getattr(self, "_doc", None) is not None:
            self._doc.close()
            self._doc = None

    # --- Eigenschaften ---
    @property
    def page_count(self) -> int:
        return self._doc.page_count

    # --- intern ---
    def _require_page(self, index: int):
        if index < 0 or index >= self.page_count:
            raise PdfError(
                ErrorCode.PDF_PAGE_OUT_OF_RANGE,
                context={"page": index, "page_count": self.page_count},
            )
        return self._doc[index]

    # --- Extraktion ---
    def extract_page(self, index: int) -> str:
        """Liefert den reinen Text einer Seite (0-basiert)."""
        page = self._require_page(index)
        return page.get_text("text")

    def extract_range(self, page_range: PageRange) -> list[PageText]:
        """Extrahiert den Text fuer alle Seiten eines Bereichs."""
        if page_range.end >= self.page_count:
            raise PdfError(
                ErrorCode.PDF_PAGE_OUT_OF_RANGE,
                context={
                    "requested_end": page_range.end,
                    "page_count": self.page_count,
                },
            )
        return [PageText(pdf_page=i, text=self.extract_page(i)) for i in page_range.pages()]

    def search_rects(self, index: int, quote: str) -> list[Rect]:
        """Sucht ein Textfragment und liefert dessen Trefferrechtecke.

        Wird zur spaeteren Platzierung von Highlights/Kommentaren genutzt.
        """
        if not quote.strip():
            return []
        page = self._require_page(index)
        return [tuple(r) for r in page.search_for(quote)]

    def paragraph_label(self, index: int, rects: list[Rect]) -> str:
        """Bestimmt einen Absatz-Hinweis fuer eine Trefferposition.

        Nutzt die Textbloecke der Seite; der Block, der die erste Trefferstelle
        vertikal enthaelt, liefert die Absatznummer (1-basiert).
        """
        if not rects:
            return ""
        page = self._require_page(index)
        target_y = rects[0][1]
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, _text, block_no, *_ = block
            if y0 <= target_y <= y1:
                return f"Absatz {int(block_no) + 1}"
        return ""

    def build_document_info(self, page_offset: int = 0) -> DocumentInfo:
        """Erzeugt die Dokument-Metadaten inkl. Seiten-Mapping."""
        return DocumentInfo(
            path=str(self.path),
            page_count=self.page_count,
            page_mapping=PageMapping(offset=page_offset),
        )
