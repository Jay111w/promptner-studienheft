"""Rohtext (z. B. aus einem Studienheft-PDF) in tokenisierte, leere Saetze zerlegen.

Grundlage fuer die manuelle Annotation. Bewusst einfach gehalten: Regex-Satzgrenzen,
Wort-/Satzzeichen-Tokens, Zeilenumbruch-Trennungen werden zusammengefuegt.

Studienhefte tragen auf jeder Seite dieselbe Kopf- oder Fusszeile. Sie landet mitten im
Fliesstext und zerschneidet Saetze, deshalb raeumt ``strip_repeated_lines`` sie vorher weg.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

from promptner.domain import Sentence

_HYPHEN_BREAK = re.compile(r"(\w)[\-­]\s*\n\s*(\w)")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_TOKEN = re.compile(r"\w+(?:[-']\w+)*|[^\w\s]", re.UNICODE)
_PAGE_NUMBER = re.compile(r"^[\s\-–—]*\d{1,4}[\s\-–—]*$")
_DIGITS = re.compile(r"\d+")


def strip_repeated_lines(pages: Iterable[str], *, min_pages: int = 3) -> str:
    """Entfernt Kopf-, Fuss- und Seitenzahlzeilen und fuegt die Seiten zu einem Text.

    Als laufender Kolumnentitel gilt eine Zeile, die auf mindestens ``min_pages`` Seiten
    steht - einmal um die Ziffern bereinigt, weil die Seitenzahl darin mitwandert. Danach
    werden Silbentrennungen wieder zusammengezogen, auch ueber die entfernte Zeile hinweg.
    """
    seiten = [p for p in pages]
    if not seiten:
        return ""

    def schluessel(zeile: str) -> str:
        return _DIGITS.sub("", zeile).strip()

    haeufigkeit = Counter(
        schluessel(z)
        for seite in seiten
        for z in {zeile.strip() for zeile in seite.splitlines() if zeile.strip()}
    )

    behalten: list[str] = []
    for seite in seiten:
        for zeile in seite.splitlines():
            roh = zeile.strip()
            if not roh or _PAGE_NUMBER.match(roh):
                continue
            k = schluessel(roh)
            if k and haeufigkeit[k] >= min_pages and len(k.split()) <= 12:
                continue
            behalten.append(roh)
    return _HYPHEN_BREAK.sub(r"\1\2", "\n".join(behalten))


def segment_text(text: str, *, source: str, min_tokens: int = 3) -> list[Sentence]:
    """Zerlegt Text in Saetze ohne Spans; sehr kurze Fragmente werden verworfen."""
    joined = _HYPHEN_BREAK.sub(r"\1\2", text)
    flat = re.sub(r"\s+", " ", joined).strip()
    sentences: list[Sentence] = []
    for raw in _SENTENCE_END.split(flat):
        tokens = _TOKEN.findall(raw)
        if len(tokens) < min_tokens:
            continue
        sentences.append(Sentence(id=f"{source}-{len(sentences)}", tokens=tokens, source=source))
    return sentences
