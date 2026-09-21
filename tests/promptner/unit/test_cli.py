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
