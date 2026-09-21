"""Konvertierung zwischen IOB2-Tags und Spans.

Lenient wie seqeval: ein ``I-X`` ohne passendes vorheriges ``B-X``/``I-X``
beginnt einen neuen Span.
"""

from __future__ import annotations

from promptner.domain import Span
from promptner.errors import DataError, ErrorCode


def _split(tag: str) -> tuple[str, str | None]:
    if tag == "O":
        return "O", None
    if len(tag) > 2 and tag[1] == "-" and tag[0] in "BI":
        return tag[0], tag[2:]
    raise DataError(ErrorCode.INVALID_BIO_SEQUENCE, f"Ungueltiges Tag: {tag!r}")


def bio_to_spans(tags: list[str]) -> list[Span]:
    spans: list[Span] = []
    start: int | None = None
    label: str | None = None
    for i, tag in enumerate(tags):
        prefix, lab = _split(tag)
        continues = prefix == "I" and start is not None and lab == label
        if not continues and start is not None:
            spans.append(Span(start=start, end=i, label=label))  # type: ignore[arg-type]
            start, label = None, None
        if prefix == "B" or (prefix == "I" and not continues):
            start, label = i, lab
    if start is not None:
        spans.append(Span(start=start, end=len(tags), label=label))  # type: ignore[arg-type]
    return spans


def spans_to_bio(spans: list[Span], n_tokens: int) -> list[str]:
    tags = ["O"] * n_tokens
    for sp in spans:
        tags[sp.start] = f"B-{sp.label}"
        for i in range(sp.start + 1, sp.end):
            tags[i] = f"I-{sp.label}"
    return tags
