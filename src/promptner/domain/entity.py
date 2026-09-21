"""Kern-Datenmodelle: Span und Sentence.

Spans sind Token-Indizes (``end`` exklusiv). Ein Satz validiert seine Spans
(Bereich, keine Ueberlappung) und sortiert sie nach ``start``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from promptner.errors import DataError, ErrorCode

LABELS_CONLL: tuple[str, ...] = ("PER", "ORG", "LOC", "MISC")
LABELS_GERMEVAL: tuple[str, ...] = ("PER", "ORG", "LOC", "OTH")


class Span(BaseModel):
    """Ein Entitaets-Span ueber Token-Indizes [start, end)."""

    model_config = {"frozen": True}

    start: int = Field(..., ge=0)
    end: int = Field(..., gt=0)
    label: str = Field(..., min_length=1)

    def text(self, tokens: list[str]) -> str:
        return " ".join(tokens[self.start : self.end])


class Sentence(BaseModel):
    """Ein tokenisierter Satz mit Gold-Spans."""

    id: str
    tokens: list[str] = Field(..., min_length=1)
    spans: list[Span] = Field(default_factory=list)
    source: str = ""

    @model_validator(mode="after")
    def _validate_spans(self) -> Sentence:
        n = len(self.tokens)
        ordered = sorted(self.spans, key=lambda s: (s.start, s.end))
        prev_end = 0
        for sp in ordered:
            if sp.start >= sp.end or sp.end > n:
                raise DataError(
                    ErrorCode.INVALID_BIO_SEQUENCE,
                    f"Span [{sp.start}, {sp.end}) liegt ausserhalb des Satzes ({n} Tokens).",
                    context={"id": self.id},
                )
            if sp.start < prev_end:
                raise DataError(
                    ErrorCode.INVALID_BIO_SEQUENCE,
                    f"Spans ueberlappen bei Token {sp.start}.",
                    context={"id": self.id},
                )
            prev_end = sp.end
        self.spans = ordered
        return self

    @property
    def text(self) -> str:
        return " ".join(self.tokens)

    def bio_tags(self) -> list[str]:
        from promptner.data.bio import spans_to_bio  # zyklischen Import vermeiden

        return spans_to_bio(self.spans, len(self.tokens))
