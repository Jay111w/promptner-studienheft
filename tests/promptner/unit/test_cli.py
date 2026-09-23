"""Unit-Tests fuer die promptner-CLI (dry-run, ohne Netz)."""

import pytest
from typer.testing import CliRunner

from promptner.cli import app


@pytest.mark.unit
def test_run_dry_run_lists_planned_runs():
    r = CliRunner().invoke(
        app,
        [
            "run",
            "--experiment",
            "E4",
            "--models",
            "m1",
            "--seeds",
            "1,2,3",
            "--limit",
            "20",
            "--dry-run",
        ],
    )
    assert r.exit_code == 0, r.output
    assert "6 Laeufe" in r.output and "def0" in r.output and "def1" in r.output


@pytest.mark.unit
def test_run_requires_models_when_no_default(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    r = CliRunner().invoke(app, ["run", "--experiment", "E5", "--dry-run", "--limit", "5"])
    assert r.exit_code == 0 and "meta-llama-3.1-8b-instruct" in r.output


@pytest.mark.unit
def test_agreement_writes_report_and_prints_numbers(tmp_path):
    import json

    def write(name: str, label: str) -> str:
        p = tmp_path / name
        row = {
            "id": "s-0",
            "tokens": ["Die", "EU", "tagt", "."],
            "spans": [{"start": 1, "end": 2, "label": label}],
            "source": "studienheft",
        }
        p.write_text(json.dumps(row) + "\n", encoding="utf-8")
        return str(p)

    out = tmp_path / "agreement.md"
    r = CliRunner().invoke(
        app,
        [
            "agreement",
            "--a",
            write("a.jsonl", "ORG"),
            "--b",
            write("b.jsonl", "LOC"),
            "--out",
            str(out),
        ],
    )
    assert r.exit_code == 0, r.output
    assert "Span-F1            0.000" in r.output
    assert "uneinige Saetze    1" in r.output
    assert "s-0" in out.read_text(encoding="utf-8")
