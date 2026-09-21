"""Datenmodelle rund um das zu pruefende Dokument.

Unterstuetzt kapitelweises Arbeiten ueber manuell gewaehlte Seitenbereiche
sowie die Abbildung PDF-Seite -> gedruckte Studienheft-Seite.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class PageRange(BaseModel):
    """Ein zusammenhaengender Seitenbereich (0-basiert, inklusive)."""

    start: int = Field(..., ge=0, description="Erste PDF-Seite (0-basiert)")
    end: int = Field(..., ge=0, description="Letzte PDF-Seite (0-basiert, inkl.)")

    @model_validator(mode="after")
    def _check_order(self) -> PageRange:
        if self.end < self.start:
            raise ValueError("end darf nicht kleiner als start sein")
        return self

    def pages(self) -> range:
        return range(self.start, self.end + 1)

    def __len__(self) -> int:
        return self.end - self.start + 1


class Chapter(BaseModel):
    """Ein Kapitel/Abschnitt, definiert ueber einen Seitenbereich."""

    title: str = Field(default="", description="Bezeichnung des Kapitels")
    page_range: PageRange


class PageMapping(BaseModel):
    """Abbildung zwischen PDF-Seitenindex und gedruckter Heft-Seitenzahl.

    Beispiel: Beginnt der gedruckte Text (Heft-Seite 1) auf PDF-Seite 3,
    dann ist ``offset = 1 - 3 = -2``.
    """

    offset: int = Field(
        default=0,
        description="printed_page = pdf_page (0-basiert) + 1 + offset",
    )

    def to_printed(self, pdf_page: int) -> int:
        """Rechnet einen 0-basierten PDF-Seitenindex in die Heft-Seite um."""
        return pdf_page + 1 + self.offset


class DocumentInfo(BaseModel):
    """Metadaten zum geladenen PDF-Dokument."""

    path: str
    page_count: int = Field(..., ge=0)
    page_mapping: PageMapping = Field(default_factory=PageMapping)
