"""Unit-Tests fuer das Einsammeln und Aggregieren der Laufergebnisse."""

import json

import pytest

from promptner.experiments.aggregate import collect, summarize, write_summary


def _write(tmp_path, run_id, **fields):
    d = tmp_path / "runs" / run_id
    d.mkdir(parents=True)
    base = {
        "run_id": run_id,
        "experiment": "E4",
        "dataset": "conll2003",
        "split": "validation",
        "limit": 10,
        "model": "m",
        "use_definition": True,
        "k_examples": 5,
        "use_cot": True,
        "use_candidates": True,
        "output_format": "text",
        "max_retries": 1,
        "seed": 1,
        "prompt_hash": "abc",
        "f1": 0.5,
        "precision": 0.5,
        "recall": 0.5,
        "n_sentences": 10,
        "parse_fail": 0,
        "retries": 0,
        "unmatched": 0,
        "unknown_type": 0,
        "elapsed_s": 1.0,
        "n_calls": 10,
        "timestamp": "t",
        "per_type_f1": "{}",
        "resumed": False,
    }
    base.update(fields)
    (d / "summary.json").write_text(json.dumps(base))


@pytest.mark.unit
def test_collect_and_summarize_mean_std(tmp_path):
    _write(tmp_path, "r1", seed=1, f1=0.4)
    _write(tmp_path, "r2", seed=2, f1=0.6)
    _write(tmp_path, "r3", seed=1, f1=0.9, use_definition=False)
    df = collect(tmp_path)
    assert len(df) == 3
    summary = summarize(df)
    row = summary[(summary["use_definition"]) & (summary["experiment"] == "E4")].iloc[0]
    assert row["n"] == 2 and abs(row["f1_mean"] - 0.5) < 1e-9 and abs(row["f1_std"] - 0.1414) < 1e-3
    row0 = summary[~summary["use_definition"]].iloc[0]
    assert row0["n"] == 1 and row0["f1_mean"] == 0.9
    out = write_summary(tmp_path)
    assert out.is_file() and "f1_mean" in out.read_text()


@pytest.mark.unit
def test_collect_empty(tmp_path):
    assert collect(tmp_path).empty
