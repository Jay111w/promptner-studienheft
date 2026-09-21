"""Schreibt native PDF-Annotationen (Acrobat-kompatibel).

Pro Korrektur wird die Fundstelle hervorgehoben (Highlight, Farbe je nach
Kategorie A/B/C) und mit einem Kommentar versehen, der Marker, Aktion,
Korrektur und Begruendung enthaelt. Findet sich keine Position, wird ersatz-
weise eine Notiz oben auf der Seite gesetzt, damit nichts verloren geht.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from korrektor.config import get_logger
from korrektor.domain import Correction
from korrektor.errors import ErrorCode, ExportError

log = get_logger("services.export.pdf_exporter")

_FALLBACK_POINT = fitz.Point(40, 40)


def _category_color(correction: Correction) -> tuple[float, float, float]:
    """Markierungsfarbe der Korrektur als RGB (0..1) fuer PyMuPDF."""
    return tuple(channel / 255 for channel in correction.category.rgb)


def export_annotated_pdf(
    source_path: str | Path,
    corrections: list[Correction],
    output_path: str | Path,
) -> Path:
    """Erzeugt ein annotiertes PDF aus Quelle + Korrekturen.

    Args:
        source_path: Originales PDF.
        corrections: Anzuwendende Korrekturen (nur freigegebene uebergeben).
        output_path: Zielpfad des annotierten PDFs.

    Returns:
        Den Pfad des geschriebenen PDFs.

    Raises:
        ExportError: Bei Lese-/Annotations-/Schreibfehlern.
    """
    source_path = Path(source_path)
    output_path = Path(output_path)
    try:
        doc = fitz.open(source_path)
    except Exception as exc:  # noqa: BLE001
        raise ExportError(
            ErrorCode.PDF_EXPORT_FAILED,
            context={"source": str(source_path)},
            cause=exc,
        ) from exc

    try:
        for correction in corrections:
            _annotate(doc, correction)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path, garbage=4, deflate=True)
    except ExportError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ExportError(
            ErrorCode.PDF_EXPORT_FAILED,
            context={"output": str(output_path)},
            cause=exc,
        ) from exc
    finally:
        doc.close()

    log.info(
        "Annotiertes PDF geschrieben: %s (%d Korrekturen).",
        output_path.name,
        len(corrections),
    )
    return output_path


def _annotate(doc: fitz.Document, correction: Correction) -> None:
    """Setzt Highlight + Kommentar fuer eine einzelne Korrektur."""
    page = doc[correction.pdf_page]
    color = _category_color(correction)
    comment = correction.comment_text()
    rects = correction.location.rects if correction.location else []

    try:
        if rects:
            for rect in rects:
                annot = page.add_highlight_annot(fitz.Rect(rect))
                annot.set_colors(stroke=color)
                annot.set_info(title=correction.id, content=comment)
                annot.update()
        else:
            # Kein Treffer lokalisiert -> Notiz als Rueckfalloption.
            annot = page.add_text_annot(_FALLBACK_POINT, comment)
            annot.set_info(title=correction.id)
            annot.update()
    except Exception as exc:  # noqa: BLE001
        raise ExportError(
            ErrorCode.PDF_ANNOTATION_FAILED,
            context={"id": correction.id, "pdf_page": correction.pdf_page},
            cause=exc,
        ) from exc
