"""Erzeugt die automatische PDF-Dokumentation der vorgenommenen Aenderungen.

Enthaelt Titel, Erstellungsdatum, eine Zusammenfassung je Kategorie (A/B/C)
sowie eine Tabelle aller Korrekturen. Wird bei jedem Speichern/Export
zusaetzlich erzeugt.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from korrektor.config import get_logger
from korrektor.domain import Category, Correction
from korrektor.errors import ErrorCode, ExportError

log = get_logger("services.export.changelog_pdf")

_COLUMNS = ["ID", "Heft-S.", "Kat.", "Original", "Korrektur", "Begruendung"]
_COL_WIDTHS = [18 * mm, 16 * mm, 12 * mm, 60 * mm, 60 * mm, 80 * mm]


def export_changelog(
    corrections: list[Correction],
    output_path: str | Path,
    document_name: str = "",
) -> Path:
    """Schreibt die Aenderungsdokumentation als PDF.

    Raises:
        ExportError: Bei Schreibfehlern.
    """
    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            title="Aenderungsdokumentation",
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Aenderungsdokumentation", styles["Title"]),
            Paragraph(_meta_line(document_name, len(corrections)), styles["Normal"]),
            Paragraph(_summary_line(corrections), styles["Normal"]),
            Spacer(1, 6 * mm),
            _build_table(corrections, styles),
        ]
        doc.build(story)
    except Exception as exc:  # noqa: BLE001
        raise ExportError(
            ErrorCode.CHANGELOG_EXPORT_FAILED,
            context={"output": str(output_path)},
            cause=exc,
        ) from exc

    log.info("Changelog-PDF geschrieben: %s.", output_path.name)
    return output_path


def _meta_line(document_name: str, count: int) -> str:
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    name = f"Dokument: {document_name} &nbsp;|&nbsp; " if document_name else ""
    return f"{name}Erstellt: {timestamp} &nbsp;|&nbsp; Korrekturen: {count}"


def _summary_line(corrections: list[Correction]) -> str:
    counts = Counter(c.category for c in corrections)
    return (
        f"Kategorie A: {counts.get(Category.A, 0)} &nbsp;|&nbsp; "
        f"B: {counts.get(Category.B, 0)} &nbsp;|&nbsp; "
        f"C: {counts.get(Category.C, 0)}"
    )


def _build_table(corrections: list[Correction], styles) -> Table:
    cell = styles["BodyText"]
    data = [_COLUMNS]
    for c in corrections:
        printed = str(c.printed_page) if c.printed_page is not None else "-"
        data.append(
            [
                Paragraph(c.id, cell),
                Paragraph(printed, cell),
                Paragraph(c.category.value, cell),
                Paragraph(c.original_text or "-", cell),
                Paragraph(c.corrected_text or "-", cell),
                Paragraph(c.reason or c.description or "-", cell),
            ]
        )
    table = Table(data, colWidths=_COL_WIDTHS, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
            ]
        )
    )
    return table
