"""Kern-Datenmodelle der Korrektur.

Das :class:`Correction`-Objekt ist die zentrale Einheit, die PDF-Annotation
und Word-Tabellenzeile ueber eine gemeinsame :attr:`Correction.id`
(z. B. ``K-001``) eindeutig verknuepft.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    """Fehlerkategorien gemaess Korrektorat-Vorgaben."""

    A = "A"  # sicherer Fehler (Rechtschreibung, Grammatik, Zeichensetzung)
    B = "B"  # klare sprachliche Verbesserung
    C = "C"  # Stil- oder Redaktionsentscheidung

    @property
    def label(self) -> str:
        return _CATEGORY_LABELS[self]

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Markierungsfarbe der Kategorie als RGB (0..255).

        Gelb = A, Blau = B, Gruen = C.
        """
        return _CATEGORY_RGB[self]


_CATEGORY_LABELS: dict[Category, str] = {
    Category.A: "Sicherer Fehler",
    Category.B: "Sprachliche Verbesserung",
    Category.C: "Stil-/Redaktionsentscheidung",
}

# Zentrale Farbzuordnung (gilt fuer PDF-Markierung UND Vorschau).
_CATEGORY_RGB: dict[Category, tuple[int, int, int]] = {
    Category.A: (255, 214, 0),  # Gelb
    Category.B: (33, 150, 243),  # Blau
    Category.C: (76, 175, 80),  # Gruen
}


class ActionType(str, Enum):
    """Art der Korrekturaktion (analog zum Lektorats-Workflow)."""

    DELETE = "streichen"
    REPLACE = "ersetzen durch"
    INSERT_AFTER = "einfuegen nach"
    INSERT_BEFORE = "einfuegen vor"


class CorrectionStatus(str, Enum):
    """Bearbeitungsstatus eines Korrekturvorschlags im Review."""

    PROPOSED = "vorgeschlagen"
    APPROVED = "freigegeben"
    REJECTED = "verworfen"
    EDITED = "bearbeitet"


class TextLocation(BaseModel):
    """Position der fehlerhaften Stelle im PDF (fuer die Annotation)."""

    pdf_page: int = Field(..., ge=0, description="0-basierter PDF-Seitenindex")
    # Trefferkoordinaten (PyMuPDF-Rechtecke), optional bis zur Lokalisierung.
    rects: list[tuple[float, float, float, float]] = Field(default_factory=list)
    quote: str = Field(default="", description="Der zu suchende Originaltext")


class Correction(BaseModel):
    """Ein einzelner Korrekturvorschlag.

    Verbindet die Markierung im PDF mit der Zeile im Word-Dokument.
    """

    id: str = Field(..., description="Eindeutiger Marker, z. B. 'K-001'")

    # --- Seitenreferenz (beide, wie gewuenscht) ---
    pdf_page: int = Field(..., ge=0, description="0-basierter PDF-Seitenindex")
    printed_page: int | None = Field(default=None, description="Gedruckte Studienheft-Seitenzahl")
    paragraph: str = Field(default="", description="Absatz/Abschnitt-Hinweis")

    # --- Inhalt ---
    original_text: str = Field(..., description="Urspruenglicher (fehlerhafter) Text")
    corrected_text: str = Field(default="", description="Korrigierter Text")

    # --- Klassifikation ---
    category: Category
    action_type: ActionType

    # --- Erklaerung ---
    description: str = Field(default="", description="Welcher Fehler liegt vor")
    reason: str = Field(default="", description="Warum ist der Fehler problematisch")
    editorial_note: str = Field(default="", description="Zusatzhinweis der Redaktion")

    # --- Technik / Workflow ---
    location: TextLocation | None = Field(default=None)
    status: CorrectionStatus = Field(default=CorrectionStatus.PROPOSED)

    def comment_text(self) -> str:
        """Formatierter Kommentartext fuer die PDF-Annotation."""
        lines = [
            f"[{self.id}] Kategorie {self.category.value} – {self.category.label}",
            f"Aktion: {self.action_type.value}",
        ]
        if self.corrected_text:
            lines.append(f"Korrektur: {self.corrected_text}")
        if self.description:
            lines.append(f"Fehler: {self.description}")
        if self.reason:
            lines.append(f"Begruendung: {self.reason}")
        if self.editorial_note:
            lines.append(f"Hinweis: {self.editorial_note}")
        return "\n".join(lines)


def make_correction_id(index: int) -> str:
    """Erzeugt eine konsistente Korrektur-ID, z. B. ``K-001``."""
    return f"K-{index:03d}"
