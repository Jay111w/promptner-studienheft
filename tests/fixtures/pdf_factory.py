"""Hilfsfunktion zum Erzeugen einfacher Test-PDFs zur Laufzeit.

So bleiben keine Binaerdateien im Repository und die Tests sind
reproduzierbar.
"""

from __future__ import annotations

from pathlib import Path

import fitz


def make_pdf(path: Path, pages: list[str]) -> Path:
    """Erzeugt ein PDF mit je einer Textseite pro Listeneintrag.

    Args:
        path: Zielpfad der PDF-Datei.
        pages: Eine Textzeile/-block je Seite.

    Returns:
        Den Pfad der erzeugten Datei.
    """
    doc = fitz.open()
    for content in pages:
        page = doc.new_page()
        page.insert_text((72, 72), content, fontsize=12)
    doc.save(path)
    doc.close()
    return path
