"""Span-Level-Evaluation mit seqeval (strict, IOB2).

Token-Accuracy waere irrefuehrend (fast alles ist ``O``); bewertet wird, ob
ein Span exakt mit Grenzen und Typ getroffen wurde.
"""

from __future__ import annotations

from pydantic import BaseModel
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2

from promptner.data.bio import spans_to_bio
from promptner.domain import Sentence, Span
from promptner.errors import DataError, ErrorCode


class TypeScore(BaseModel):
    precision: float
    recall: float
    f1: float
    support: int


class EvalResult(BaseModel):
    precision: float
    recall: float
    f1: float
    n_sentences: int
    per_type: dict[str, TypeScore]


def evaluate(gold: list[Sentence], predicted: list[list[Span]]) -> EvalResult:
    """Micro-P/R/F1 auf Span-Ebene plus Werte je Entitaetstyp."""
    if len(gold) != len(predicted):
        raise DataError(
            ErrorCode.EVAL_FAILED,
            f"{len(gold)} Gold-Saetze, aber {len(predicted)} Vorhersagen.",
        )
    y_true = [s.bio_tags() for s in gold]
    y_pred = [spans_to_bio(p, len(s.tokens)) for s, p in zip(gold, predicted, strict=True)]
    report = classification_report(
        y_true, y_pred, mode="strict", scheme=IOB2, output_dict=True, zero_division=0
    )
    micro = report["micro avg"]
    per_type = {
        label: TypeScore(
            precision=float(v["precision"]),
            recall=float(v["recall"]),
            f1=float(v["f1-score"]),
            support=int(v["support"]),
        )
        for label, v in report.items()
        if not label.endswith(" avg")
    }
    return EvalResult(
        precision=float(micro["precision"]),
        recall=float(micro["recall"]),
        f1=float(micro["f1-score"]),
        n_sentences=len(gold),
        per_type=per_type,
    )
