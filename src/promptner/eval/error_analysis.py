"""Fehleranalyse auf gespeicherten Laeufen (Phase 5; kein API-Aufruf).

Jeder Gold-/Pred-Span wird einer Klasse zugeordnet (correct, type, boundary, boundary+type,
missed, spurious). Daraus entstehen Verwechslungsmatrix Gold x Pred (mit ``O`` fuer
"kein Span"), Zaehler je Klasse und Typ sowie markierte Beispielsaetze fuer den Bericht.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from promptner.domain import Span

Kind = str  # correct | type | boundary | boundary+type | missed | spurious
NONE = "O"  # "kein Span" in der Matrix


@dataclass(frozen=True)
class SpanError:
    kind: Kind
    gold: Span | None
    pred: Span | None

    @property
    def gold_label(self) -> str | None:
        return self.gold.label if self.gold else None

    @property
    def pred_label(self) -> str | None:
        return self.pred.label if self.pred else None


@dataclass
class Example:
    sentence_id: str
    tokens: list[str]
    errors: list[SpanError]
    parse_ok: bool
    candidates: list[dict]


@dataclass
class ErrorReport:
    run_id: str
    n_sentences: int
    n_parse_fail: int
    n_retries: int
    n_unmatched: int
    n_unknown_type: int
    counts: Counter = field(default_factory=Counter)  # je Klasse
    by_type: dict[str, Counter] = field(default_factory=dict)  # Gold-Typ -> Klasse -> n
    matrix: Counter = field(default_factory=Counter)  # (gold_label|O, pred_label|O) -> n
    examples: list[Example] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


def _overlaps(a: Span, b: Span) -> bool:
    return a.start < b.end and b.start < a.end


def classify_sentence(tokens: list[str], gold: list[Span], pred: list[Span]) -> list[SpanError]:
    """Paart Gold- und Pred-Spans: exakte Grenzen zuerst, dann Ueberlappung; Rest missed/spurious."""
    out: list[SpanError] = []
    free_pred = list(pred)
    unmatched_gold: list[Span] = []
    for g in gold:
        exact = next((p for p in free_pred if p.start == g.start and p.end == g.end), None)
        if exact is not None:
            free_pred.remove(exact)
            out.append(SpanError("correct" if exact.label == g.label else "type", g, exact))
        else:
            unmatched_gold.append(g)
    for g in unmatched_gold:
        partner = next((p for p in free_pred if _overlaps(p, g)), None)
        if partner is None:
            out.append(SpanError("missed", g, None))
            continue
        free_pred.remove(partner)
        kind = "boundary" if partner.label == g.label else "boundary+type"
        out.append(SpanError(kind, g, partner))
    out.extend(SpanError("spurious", None, p) for p in free_pred)
    out.sort(key=lambda e: (e.gold or e.pred).start)  # type: ignore[union-attr]
    return out


def _load_rows(run_dir: Path) -> list[dict]:
    with (run_dir / "predictions.jsonl").open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def analyze_run(run_dir: str | Path) -> ErrorReport:
    run_dir = Path(run_dir)
    rows = _load_rows(run_dir)
    summary_path = run_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    rep = ErrorReport(
        run_id=summary.get("run_id", run_dir.name),
        n_sentences=len(rows),
        n_parse_fail=sum(1 for r in rows if not r.get("parse_ok", True)),
        n_retries=sum(int(r.get("retries", 0)) for r in rows),
        n_unmatched=sum(int(r.get("n_unmatched", 0)) for r in rows),
        n_unknown_type=sum(int(r.get("n_unknown_type", 0)) for r in rows),
        summary=summary,
    )
    for r in rows:
        gold = [Span(**s) for s in r["gold"]]
        pred = [Span(**s) for s in r["pred"]]
        errors = classify_sentence(r["tokens"], gold, pred)
        for e in errors:
            rep.counts[e.kind] += 1
            rep.matrix[(e.gold_label or NONE, e.pred_label or NONE)] += 1
            if e.gold is not None:
                rep.by_type.setdefault(e.gold.label, Counter())[e.kind] += 1
        if not r.get("parse_ok", True) or any(e.kind != "correct" for e in errors):
            rep.examples.append(
                Example(
                    sentence_id=r["sentence_id"],
                    tokens=r["tokens"],
                    errors=errors,
                    parse_ok=r.get("parse_ok", True),
                    candidates=r.get("candidates", []),
                )
            )
    return rep


def mark_sentence(tokens: list[str], errors: list[SpanError]) -> str:
    """Satz mit ``[Text]{GOLD→PRED}``-Markierungen; korrekte Spans als ``[Text]{LOC}``."""
    marks: dict[int, tuple[int, str]] = {}
    for e in errors:
        span = e.gold or e.pred
        assert span is not None
        if e.kind == "correct":
            tag = e.gold_label or ""
        else:
            tag = f"{e.gold_label or NONE}→{e.pred_label or NONE}"
        # bei Grenzfehlern beide Spans zeigen: Gold-Grenzen, Pred-Grenzen in der Markierung
        if e.kind.startswith("boundary") and e.pred is not None and e.gold is not None:
            tag += f" pred=„{' '.join(tokens[e.pred.start : e.pred.end])}“"
        marks.setdefault(span.start, (span.end, tag))
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if i in marks:
            end, tag = marks[i]
            out.append(f"[{' '.join(tokens[i:end])}]{{{tag}}}")
            i = end
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


_KIND_DE = {
    "correct": "korrekt",
    "type": "Typverwechslung (Grenzen richtig)",
    "boundary": "Grenzfehler (Typ richtig)",
    "boundary+type": "Grenz- und Typfehler",
    "missed": "übersehen",
    "spurious": "erfunden / falsch positiv",
}


def render_markdown(rep: ErrorReport, *, max_examples: int = 10) -> str:
    labels = sorted(({g for g, _ in rep.matrix} | {p for _, p in rep.matrix}) - {NONE})
    cols = labels + [NONE]
    lines = [f"# Fehleranalyse – `{rep.run_id}`", ""]
    if rep.summary:
        lines.append(
            f"F1 {rep.summary.get('f1', 0):.3f} · P {rep.summary.get('precision', 0):.3f} · "
            f"R {rep.summary.get('recall', 0):.3f} · Modell `{rep.summary.get('model', '?')}`"
        )
        lines.append("")
    lines += ["## Kennzahlen", "", "| Größe | n |", "|---|---|"]
    lines.append(f"| Sätze | {rep.n_sentences} |")
    for kind, name in _KIND_DE.items():
        lines.append(f"| {name} | {rep.counts.get(kind, 0)} |")
    lines.append(f"| Halluzinierte Kandidaten (nicht im Text) | {rep.n_unmatched} |")
    lines.append(f"| Unbekannte Typnamen | {rep.n_unknown_type} |")
    lines.append(f"| Format-Fehler (parse_ok=false) | {rep.n_parse_fail} |")
    lines.append(f"| Retries | {rep.n_retries} |")
    lines += ["", "## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)", ""]
    lines.append("| Gold \\ Pred | " + " | ".join(cols) + " |")
    lines.append("|---|" + "---|" * len(cols))
    for g in cols:
        lines.append(f"| {g} | " + " | ".join(str(rep.matrix.get((g, p), 0)) for p in cols) + " |")
    lines += [
        "",
        "## Fehler je Gold-Typ",
        "",
        "| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |",
        "|---|---|---|---|---|---|",
    ]
    for t in labels:
        c = rep.by_type.get(t, Counter())
        lines.append(
            f"| {t} | {c.get('correct', 0)} | {c.get('type', 0)} | {c.get('boundary', 0)} | "
            f"{c.get('boundary+type', 0)} | {c.get('missed', 0)} |"
        )
    lines += ["", f"## Beispiele (max. {max_examples}; `[Text]{{GOLD→PRED}}`)", ""]
    for ex in rep.examples[:max_examples]:
        flag = "" if ex.parse_ok else " ⚠️ Format-Fehler"
        lines.append(f"- `{ex.sentence_id}`{flag}: {mark_sentence(ex.tokens, ex.errors)}")
    lines.append("")
    return "\n".join(lines)


def write_report(run_dir: str | Path, out: str | Path, *, max_examples: int = 10) -> Path:
    rep = analyze_run(run_dir)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(rep, max_examples=max_examples), encoding="utf-8")
    return out
