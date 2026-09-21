"""Rohtext (z. B. aus einem Studienheft-PDF) in tokenisierte, leere Saetze zerlegen.

Grundlage fuer die manuelle Annotation. Bewusst einfach gehalten: Regex-Satzgrenzen,
Wort-/Satzzeichen-Tokens, Zeilenumbruch-Trennungen werden zusammengefuegt.
"""

from __future__ import annotations

import re

from promptner.domain import Sentence

_HYPHEN_BREAK = re.compile(r"(\w)[\-­]\s*\n\s*(\w)")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_TOKEN = re.compile(r"\w+(?:[-']\w+)*|[^\w\s]", re.UNICODE)


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
