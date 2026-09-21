"""Unit-Tests fuer run_spec/run_all mit Fake-Client und gepatchtem Loader."""

import json

import pytest

from promptner.domain import PromptConfig, Sentence, Span
from promptner.experiments import runner as runner_module
from promptner.experiments.runner import RunRecord, run_all, run_spec
from promptner.experiments.spec import RunSpec
from promptner.llm.client import LlmClient

SENTS = [
    Sentence(id="a", tokens=["Ohio", "is", "big"], spans=[Span(start=0, end=1, label="LOC")]),
    Sentence(id="b", tokens=["Nothing", "here"], spans=[]),
]
GOOD = {"a": "1. Ohio | True | a state (location)\n2. big | False | adjective", "b": "None"}


class _FakeClient(LlmClient):
    def __init__(self):
        self.calls_made = 0

    def complete(self, request):
        self.calls_made += 1
        for sid, ans in GOOD.items():
            if request.user.rstrip().endswith(
                f"Paragraph: {' '.join(next(s.tokens for s in SENTS if s.id == sid))}\n\nAnswer:"
            ):
                return ans
        return "None"


@pytest.fixture
def spec(monkeypatch):
    monkeypatch.setattr(
        runner_module,
        "load_sentences",
        lambda dataset, split, limit: SENTS[:limit] if limit else SENTS,
    )
    return RunSpec(
        "E4",
        "conll2003",
        "validation",
        2,
        "fake-model",
        PromptConfig(dataset="conll2003", k_examples=2),
    )


@pytest.mark.unit
def test_run_spec_writes_files_and_metrics(spec, tmp_path):
    client = _FakeClient()
    rec = run_spec(spec, client=client, cache=None, results_dir=tmp_path, workers=1)
    assert isinstance(rec, RunRecord)
    assert rec.f1 == 1.0 and rec.n_sentences == 2 and rec.n_calls == 2
    assert rec.experiment == "E4" and rec.model == "fake-model" and rec.seed == 1
    run_dir = tmp_path / "runs" / spec.run_id
    assert (run_dir / "summary.json").is_file()
    lines = (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and json.loads(lines[0])["sentence_id"] == "a"
    assert json.loads((run_dir / "summary.json").read_text())["f1"] == 1.0


@pytest.mark.unit
def test_run_spec_resumes_without_api_calls(spec, tmp_path):
    run_spec(spec, client=_FakeClient(), cache=None, results_dir=tmp_path, workers=1)
    client = _FakeClient()
    rec = run_spec(spec, client=client, cache=None, results_dir=tmp_path, workers=1)
    assert client.calls_made == 0 and rec.f1 == 1.0 and rec.resumed is True


@pytest.mark.unit
def test_run_all_returns_records_in_order(spec, tmp_path):
    other = RunSpec(
        "E4",
        "conll2003",
        "validation",
        2,
        "fake-model",
        PromptConfig(dataset="conll2003", k_examples=2, use_definition=False),
    )
    recs = run_all([spec, other], client=_FakeClient(), cache=None, results_dir=tmp_path, workers=1)
    assert [r.run_id for r in recs] == [spec.run_id, other.run_id]
