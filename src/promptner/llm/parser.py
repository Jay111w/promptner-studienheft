"""Parst die LLM-Antwort in Kandidaten und richtet sie auf Token-Spans aus.

Textformat (Figure 1): ``N. <Text> | True/False | <Begruendung> (<Typ>)``.
Ohne CoT: ``N. <Text> | True (<Typ>)``. JSON-Format: ``{"candidates": [...]}``.
Alignment sucht jedes Kandidaten-Vorkommen als Token-Teilfolge; bei
Ueberlappungen gewinnt der laengere Span. Nicht auffindbare Texte und unbekannte
Typen werden gezaehlt (Fehleranalyse), nicht geraten.
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, ValidationError

from promptner.config import get_logger
from promptner.domain import Candidate, PromptConfig, Sentence, Span
from promptner.errors import ErrorCode, ParseError
from promptner.prompting.definitions import resolve_type

log = get_logger("llm.parser")

_LINE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?\d+[.)]?(?:\*\*)?\s*(.+)$")
_TYPE_SUFFIX = re.compile(r"\(([^()]+)\)\s*[.]?\s*$")
_TRUE = {"true", "yes", "ja", "wahr"}
_FALSE = {"false", "no", "nein", "falsch"}
_NONE = {"none", "keine", "no entities", "keine entitäten", "-"}


class _JsonCandidate(BaseModel):
    text: str
    is_entity: bool
    explanation: str = ""
    type_name: str | None = None


class _JsonAnswer(BaseModel):
    candidates: list[_JsonCandidate]


def _clean(s: str) -> str:
    return s.strip().strip("*`\"'“”„ ").strip()


def _parse_text(raw: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    saw_list = False
    for line in raw.splitlines():
        m = _LINE.match(line)
        if not m or "|" not in m.group(1):
            continue
        saw_list = True
        fields = [f.strip() for f in m.group(1).split("|")]
        text = _clean(fields[0])
        decision = fields[1] if len(fields) > 1 else ""
        rest = " | ".join(fields[2:]) if len(fields) > 2 else ""
        # Typ steht in Klammern am Ende der Begruendung (mit CoT) oder der Entscheidung (ohne CoT)
        type_name = None
        for holder in (rest, decision):
            tm = _TYPE_SUFFIX.search(holder)
            if tm:
                type_name = tm.group(1).strip()
                break
        flag = decision.split("(")[0].strip().strip(".").lower()
        if flag in _TRUE:
            is_entity = True
        elif flag in _FALSE:
            is_entity = False
        else:
            raise ParseError(ErrorCode.RESPONSE_INVALID, f"Unklare Entscheidung: {decision!r}")
        explanation = _TYPE_SUFFIX.sub("", rest).strip().rstrip(".").strip()
        if not text:
            continue
        candidates.append(
            Candidate(
                text=text,
                is_entity=is_entity,
                explanation=explanation,
                type_name=type_name if is_entity else None,
            )
        )
    if not saw_list:
        stripped = raw.strip().lower()
        stripped = re.sub(r"^(answer|antwort):\s*", "", stripped).strip()
        if stripped in _NONE:
            return []
        raise ParseError(ErrorCode.RESPONSE_INVALID, "Keine Kandidatenzeile gefunden.")
    return candidates


def _parse_json(raw: str) -> list[Candidate]:
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < 0:
        raise ParseError(ErrorCode.RESPONSE_INVALID, "Kein JSON-Objekt in der Antwort.")
    try:
        answer = _JsonAnswer.model_validate(json.loads(raw[start : end + 1]))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ParseError(
            ErrorCode.RESPONSE_INVALID, "JSON entspricht nicht dem Schema.", cause=exc
        ) from exc
    return [
        Candidate(
            text=_clean(c.text),
            is_entity=c.is_entity,
            explanation=c.explanation,
            type_name=c.type_name if c.is_entity else None,
        )
        for c in answer.candidates
        if _clean(c.text)
    ]


def parse_answer(raw: str, config: PromptConfig) -> list[Candidate]:
    """Wandelt die Rohantwort in Kandidaten um; wirft ``ParseError`` bei Formatbruch."""
    return _parse_json(raw) if config.output_format == "json" else _parse_text(raw)


def _find_all(tokens: list[str], needle: list[str]) -> list[tuple[int, int]]:
    n = len(needle)
    if n == 0 or n > len(tokens):
        return []
    return [(i, i + n) for i in range(len(tokens) - n + 1) if tokens[i : i + n] == needle]


def _tokenize_candidate(text: str) -> list[str]:
    # Satzzeichen, die im Satz eigene Tokens sind, vom Kandidaten abtrennen (z. B. "Berlin,")
    return re.findall(r"\w+(?:[-'’.]\w+)*|[^\w\s]", text, re.UNICODE)


def align(
    sentence: Sentence, candidates: list[Candidate], dataset: str
) -> tuple[list[Span], int, int]:
    """Kandidaten -> Token-Spans. Rueckgabe: (spans, n_unmatched, n_unknown_type)."""
    tokens = sentence.tokens
    lower = [t.lower() for t in tokens]
    unmatched = unknown = 0
    found: list[Span] = []
    for c in candidates:
        if not c.is_entity:
            continue
        label = resolve_type(dataset, c.type_name)
        if label is None:
            unknown += 1
            continue
        needle = _tokenize_candidate(c.text)
        while needle and needle[-1] in {",", ".", ";", ":", "!", "?"}:
            needle = needle[:-1]  # angehaengte Satzzeichen ignorieren
        hits = _find_all(tokens, needle) or _find_all(lower, [t.lower() for t in needle])
        if not hits:
            unmatched += 1
            continue
        found.extend(Span(start=a, end=b, label=label) for a, b in hits)
    # Ueberlappungen aufloesen: laengster Span zuerst, dann Position
    found.sort(key=lambda s: (-(s.end - s.start), s.start))
    taken = [False] * len(tokens)
    spans: list[Span] = []
    for sp in found:
        if any(taken[sp.start : sp.end]):
            continue
        for i in range(sp.start, sp.end):
            taken[i] = True
        spans.append(sp)
    spans.sort(key=lambda s: s.start)
    return spans, unmatched, unknown
