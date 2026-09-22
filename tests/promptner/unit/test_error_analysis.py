"""Unit-Tests fuer die Fehleranalyse (Phase 5): Klassifikation, Bericht, Markdown."""

import json

import pytest

from promptner.domain import Span
from promptner.eval.error_analysis import analyze_run, classify_sentence, render_markdown

TOK = ["At", "the", "Oval", ",", "Surrey", "beat", "Kent", "and", "Hussain", "scored", "."]


def _sp(a, b, label):
    return Span(start=a, end=b, label=label)


@pytest.mark.unit
def test_classify_all_six_classes():
    gold = [_sp(2, 3, "LOC"), _sp(4, 5, "ORG"), _sp(6, 7, "ORG"), _sp(8, 9, "PER")]
    pred = [_sp(1, 3, "LOC"), _sp(4, 5, "LOC"), _sp(9, 10, "MISC")]
    errs = classify_sentence(TOK, gold, pred)
    kinds = {(e.kind, e.gold_label, e.pred_label) for e in errs}
    assert ("boundary", "LOC", "LOC") in kinds  # "the Oval" statt "Oval"
    assert ("type", "ORG", "LOC") in kinds  # Surrey
    assert ("missed", "ORG", None) in kinds  # Kent
    assert ("missed", "PER", None) in kinds  # Hussain
    assert ("spurious", None, "MISC") in kinds  # scored
    assert len(errs) == 5


@pytest.mark.unit
def test_classify_correct_and_boundary_type():
    gold = [_sp(2, 3, "LOC"), _sp(4, 5, "ORG")]
    pred = [_sp(2, 3, "LOC"), _sp(4, 6, "PER")]
    errs = classify_sentence(TOK, gold, pred)
    assert [(e.kind, e.gold_label, e.pred_label) for e in errs] == [
        ("correct", "LOC", "LOC"),
        ("boundary+type", "ORG", "PER"),
    ]


def _write_run(tmp_path, rows):
    run_dir = tmp_path / "runs" / "E4__x"
    run_dir.mkdir(parents=True)
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    (run_dir / "summary.json").write_text(json.dumps({"run_id": "E4__x", "f1": 0.5}))
    return run_dir


def _row(sid, gold, pred, **kw):
    base = {
        "sentence_id": sid,
        "tokens": TOK,
        "gold": [s.model_dump() for s in gold],
        "pred": [s.model_dump() for s in pred],
        "candidates": [],
        "parse_ok": True,
        "retries": 0,
        "n_unmatched": 0,
        "n_unknown_type": 0,
        "raw": "",
    }
    base.update(kw)
    return base


@pytest.mark.unit
def test_analyze_run_builds_matrix_counts_and_examples(tmp_path):
    run_dir = _write_run(
        tmp_path,
        [
            _row("a", [_sp(4, 5, "ORG")], [_sp(4, 5, "LOC")], n_unmatched=2),
            _row("b", [_sp(2, 3, "LOC")], [_sp(2, 3, "LOC")]),
            _row("c", [_sp(8, 9, "PER")], [], parse_ok=False, retries=1),
        ],
    )
    rep = analyze_run(run_dir)
    assert rep.run_id == "E4__x"
    assert rep.n_sentences == 3 and rep.n_parse_fail == 1 and rep.n_unmatched == 2
    assert rep.counts["correct"] == 1 and rep.counts["type"] == 1 and rep.counts["missed"] == 1
    assert rep.matrix[("ORG", "LOC")] == 1 and rep.matrix[("PER", "O")] == 1
    assert rep.matrix[("LOC", "LOC")] == 1
    # Beispiele: nur Saetze mit Fehlern, korrekte nicht
    assert [e.sentence_id for e in rep.examples] == ["a", "c"]


@pytest.mark.unit
def test_render_markdown_contains_matrix_and_marked_example(tmp_path):
    run_dir = _write_run(
        tmp_path, [_row("a", [_sp(4, 5, "ORG"), _sp(6, 7, "ORG")], [_sp(4, 5, "LOC")])]
    )
    md = render_markdown(analyze_run(run_dir), max_examples=5)
    assert "| Gold \\ Pred |" in md and "| ORG |" in md
    assert "[Surrey]{ORG→LOC}" in md and "[Kent]{ORG→O}" in md
    assert "Typverwechslung" in md and "Halluzinierte Kandidaten" in md
    header = next(line for line in md.splitlines() if line.startswith("| Gold \\ Pred |"))
    assert header.count(" O ") == 1  # "kein Span" genau einmal, nicht als eigener Typ


@pytest.mark.unit
def test_mark_sentence_keeps_overlapping_errors_as_addendum():
    from promptner.eval.error_analysis import SpanError, mark_sentence

    errors = [
        SpanError("correct", _sp(1, 3, "LOC"), _sp(1, 3, "LOC")),
        SpanError("spurious", None, _sp(2, 4, "ORG")),
    ]
    line = mark_sentence(TOK, errors)
    assert "[the Oval]{LOC}" in line and "[Oval ,]{O→ORG}" in line
