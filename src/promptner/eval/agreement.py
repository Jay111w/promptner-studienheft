"""Uebereinstimmung zweier Annotatorinnen auf denselben Saetzen (Studienheft-Sample).

Zwei Masse, weil sie Verschiedenes zeigen:

* **Span-F1** (exakte Grenzen *und* Typ, dieselbe seqeval-Funktion wie bei den Experimenten) –
  das ist die Groesse, die im Bericht neben den Modellzahlen steht und mit ihnen vergleichbar ist.
* **Cohen's Kappa** ueber die BIO-Tags je Token – korrigiert die Uebereinstimmung um den Zufall.
  Bei NER ist das Mass optimistisch, weil die meisten Tokens ``O`` sind; es steht daneben, weil
  es die in der Literatur uebliche Zahl ist.

Dazu eine Liste der Saetze, in denen sich die beiden unterscheiden – das ist der Teil, den man
vor der Abgabe gemeinsam durchgeht.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptner.data.bio import spans_to_bio
from promptner.domain import LABELS_GERMEVAL, Sentence, Span
from promptner.errors import DataError, ErrorCode
from promptner.eval.metrics import evaluate


@dataclass(frozen=True)
class Disagreement:
    """Ein Satz, in dem sich die Span-Mengen unterscheiden."""

    sentence_id: str
    tokens: list[str]
    only_a: list[Span]
    only_b: list[Span]


@dataclass(frozen=True)
class AgreementReport:
    n_sentences: int
    n_spans_a: int
    n_spans_b: int
    span_f1: float
    per_type_f1: dict[str, float]
    token_kappa: float
    token_accuracy: float
    disagreements: list[Disagreement] = field(default_factory=list)
    unknown_labels: set[str] = field(default_factory=set)


def cohen_kappa(a: list[str], b: list[str]) -> float:
    """Cohen's Kappa fuer zwei gleich lange Tag-Folgen.

    Vergeben beide durchweg dasselbe Tag (bei NER der Normalfall ``O``), ist die Formel 0/0.
    Das ist vollstaendige Einigkeit, also 1.0.
    """
    if len(a) != len(b):
        raise DataError(
            ErrorCode.EVAL_FAILED,
            f"Tag-Folgen verschieden lang: {len(a)} gegen {len(b)}.",
        )
    if not a:
        raise DataError(ErrorCode.EVAL_FAILED, "Keine Tokens zu vergleichen.")

    n = len(a)
    observed = sum(1 for x, y in zip(a, b, strict=True) if x == y) / n
    labels = set(a) | set(b)
    expected = sum((a.count(lbl) / n) * (b.count(lbl) / n) for lbl in labels)
    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def _by_id(sentences: list[Sentence]) -> dict[str, Sentence]:
    return {s.id: s for s in sentences}


def compare(a: list[Sentence], b: list[Sentence]) -> AgreementReport:
    """Vergleicht zwei Annotationen derselben Saetze; verglichen wird die Schnittmenge der IDs."""
    map_a, map_b = _by_id(a), _by_id(b)
    common = sorted(set(map_a) & set(map_b))
    if not common:
        raise DataError(
            ErrorCode.EVAL_FAILED,
            "Die beiden Dateien haben keinen Satz gemeinsam (IDs stimmen nicht ueberein).",
        )
    for sid in common:
        if map_a[sid].tokens != map_b[sid].tokens:
            raise DataError(
                ErrorCode.EVAL_FAILED,
                f"Satz {sid} hat in beiden Dateien verschiedene Tokens - "
                "es muss dieselbe Vorlage annotiert worden sein.",
                context={"id": sid},
            )

    sents_a = [map_a[sid] for sid in common]
    result = evaluate(sents_a, [map_b[sid].spans for sid in common])

    tags_a: list[str] = []
    tags_b: list[str] = []
    disagreements: list[Disagreement] = []
    unknown: set[str] = set()
    for sid in common:
        sa, sb = map_a[sid], map_b[sid]
        tags_a.extend(spans_to_bio(sa.spans, len(sa.tokens)))
        tags_b.extend(spans_to_bio(sb.spans, len(sb.tokens)))
        unknown |= {s.label for s in [*sa.spans, *sb.spans] if s.label not in LABELS_GERMEVAL}
        set_a, set_b = set(sa.spans), set(sb.spans)
        if set_a != set_b:
            disagreements.append(
                Disagreement(
                    sentence_id=sid,
                    tokens=sa.tokens,
                    only_a=sorted(set_a - set_b, key=lambda s: s.start),
                    only_b=sorted(set_b - set_a, key=lambda s: s.start),
                )
            )

    matched = sum(1 for x, y in zip(tags_a, tags_b, strict=True) if x == y)
    return AgreementReport(
        n_sentences=len(common),
        n_spans_a=sum(len(map_a[sid].spans) for sid in common),
        n_spans_b=sum(len(map_b[sid].spans) for sid in common),
        span_f1=result.f1,
        per_type_f1={lbl: score.f1 for lbl, score in result.per_type.items()},
        token_kappa=cohen_kappa(tags_a, tags_b),
        token_accuracy=matched / len(tags_a),
        disagreements=disagreements,
        unknown_labels=unknown,
    )


def _spans_text(spans: list[Span], tokens: list[str]) -> str:
    return ", ".join(f"`{s.text(tokens)}` ({s.label})" for s in spans) or "–"


def render_markdown(rep: AgreementReport, max_examples: int = 20) -> str:
    """Bericht fuer `docs/` – Kennzahlen plus die Saetze, die gemeinsam zu klaeren sind."""
    lines = [
        "# Annotator-Uebereinstimmung (Studienheft-Sample)",
        "",
        f"- Gemeinsam annotierte Saetze: **{rep.n_sentences}**",
        f"- Spans: {rep.n_spans_a} (A) gegen {rep.n_spans_b} (B)",
        f"- **Span-F1 (exakte Grenzen und Typ): {rep.span_f1:.3f}**",
        f"- Cohen's Kappa je Token (BIO): {rep.token_kappa:.3f} "
        f"(Rohuebereinstimmung {rep.token_accuracy:.3f})",
        f"- Uneinige Saetze: {len(rep.disagreements)} von {rep.n_sentences}",
        "",
    ]
    if rep.unknown_labels:
        lines += [
            f"> **Achtung:** Labels ausserhalb von {', '.join(LABELS_GERMEVAL)}: "
            f"{', '.join(sorted(rep.unknown_labels))}. Vor dem Lauf korrigieren.",
            "",
        ]
    if rep.per_type_f1:
        lines += ["| Typ | F1 |", "|---|---|"]
        lines += [f"| {lbl} | {f1:.3f} |" for lbl, f1 in sorted(rep.per_type_f1.items())]
        lines.append("")
    if rep.disagreements:
        lines += ["## Uneinige Saetze", ""]
        for d in rep.disagreements[:max_examples]:
            lines += [
                f"**{d.sentence_id}** – {' '.join(d.tokens)}",
                "",
                f"- nur A: {_spans_text(d.only_a, d.tokens)}",
                f"- nur B: {_spans_text(d.only_b, d.tokens)}",
                "",
            ]
        if len(rep.disagreements) > max_examples:
            lines.append(f"*(… {len(rep.disagreements) - max_examples} weitere)*")
    return "\n".join(lines)
