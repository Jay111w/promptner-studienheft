"""Abbildung PDF-Seite <-> gedruckte Studienheft-Seite.

Die gedruckte Heft-Seitenzahl weicht oft vom technischen PDF-Index ab
(z. B. wegen Deckblatt/Vorwort). Dieser Dienst ermittelt und wendet den
noetigen Versatz (Offset) an, damit Word-Tabelle und PDF-Kommentare die
*gedruckte* Seitenzahl korrekt referenzieren.
"""

from __future__ import annotations

from korrektor.config import get_logger
from korrektor.domain import PageMapping

log = get_logger("services.pdf.page_mapper")


def detect_offset(pdf_page_index: int, printed_page_number: int) -> int:
    """Berechnet den Offset aus einem bekannten Referenzpunkt.

    Beispiel: Auf PDF-Seite mit Index 2 steht die gedruckte Seitenzahl 1,
    also ``offset = 1 - (2 + 1) = -2``.

    Args:
        pdf_page_index: 0-basierter PDF-Seitenindex der Referenzseite.
        printed_page_number: Die dort sichtbare gedruckte Seitenzahl.

    Returns:
        Den Offset fuer :class:`PageMapping`.
    """
    offset = printed_page_number - (pdf_page_index + 1)
    log.debug(
        "Offset ermittelt: pdf_index=%d, printed=%d -> offset=%d",
        pdf_page_index,
        printed_page_number,
        offset,
    )
    return offset


class PageMapper:
    """Wendet ein :class:`PageMapping` bequem auf PDF-Seitenindizes an."""

    def __init__(self, mapping: PageMapping | None = None) -> None:
        self.mapping = mapping or PageMapping()

    @classmethod
    def from_reference(cls, pdf_page_index: int, printed_page_number: int) -> PageMapper:
        """Erzeugt einen Mapper aus einem bekannten Referenzpunkt."""
        offset = detect_offset(pdf_page_index, printed_page_number)
        return cls(PageMapping(offset=offset))

    def printed_page(self, pdf_page_index: int) -> int:
        """Gibt die gedruckte Heft-Seitenzahl zu einem PDF-Index zurueck."""
        return self.mapping.to_printed(pdf_page_index)

    def label(self, pdf_page_index: int) -> str:
        """Lesbares Label mit beiden Seitenangaben (PDF + gedruckt)."""
        return f"PDF-Seite {pdf_page_index + 1} (Heft-Seite {self.printed_page(pdf_page_index)})"
