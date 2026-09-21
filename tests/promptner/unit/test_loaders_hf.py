"""Unit-Tests fuer die HF-Loader mit gepatchten Datenquellen (kein Netz)."""

import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from promptner.data import loaders
from promptner.domain import LABELS_CONLL, LABELS_GERMEVAL, Span

CONLL_NAMES = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]
GERMEVAL_NAMES = [
    "O",
    "B-LOC",
    "I-LOC",
    "B-LOCderiv",
    "I-LOCderiv",
    "B-PER",
    "I-PER",
    "B-OTHpart",
    "I-OTHpart",
]


class _Feature:
    def __init__(self, names):
        self.feature = type("F", (), {"names": names})()


class _FakeSplit:
    def __init__(self, rows, names):
        self._rows = rows
        self.features = {"ner_tags": _Feature(names)}

    def __len__(self):
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def select(self, idx):
        return _FakeSplit([self._rows[i] for i in idx], self.features["ner_tags"].feature.names)


@pytest.mark.unit
def test_load_conll2003_maps_labels(monkeypatch):
    rows = [
        {"tokens": ["Peter", "Blackburn"], "ner_tags": [1, 2]},
        {"tokens": ["EU", "rejects", "German", "call"], "ner_tags": [3, 0, 7, 0]},
        {"tokens": ["."], "ner_tags": [0]},
    ]
    monkeypatch.setattr(loaders, "_hf_split", lambda repo, split: _FakeSplit(rows, CONLL_NAMES))
    sents = loaders.load_conll2003("validation", limit=2)
    assert len(sents) == 2
    assert sents[0].spans == [Span(start=0, end=2, label="PER")]
    assert sents[1].spans == [Span(start=0, end=1, label="ORG"), Span(start=2, end=3, label="MISC")]
    assert sents[0].id == "conll2003-validation-0"
    assert sents[0].source == "conll2003"
    assert {sp.label for s in sents for sp in s.spans} <= set(LABELS_CONLL)


def _germeval_parquet(tmp_path):
    table = pa.table(
        {
            "id": ["0", "1"],
            "source": ["wiki", "wiki"],
            "tokens": [["Wolf", "Bree", "war", "deutscher"], ["Berlin", "liegt"]],
            "ner_tags": [[5, 6, 0, 3], [1, 0]],
            "nested_ner_tags": [[0, 0, 0, 0], [0, 0]],
        }
    )
    meta = {"info": {"features": {"ner_tags": {"feature": {"names": GERMEVAL_NAMES}}}}}
    table = table.replace_schema_metadata({b"huggingface": json.dumps(meta).encode()})
    p = tmp_path / "germeval.parquet"
    pq.write_table(table, p)
    return p


@pytest.mark.unit
def test_load_germeval14_drops_subtypes_by_default(monkeypatch, tmp_path):
    p = _germeval_parquet(tmp_path)
    monkeypatch.setattr(loaders, "_germeval_parquet_path", lambda split: p)
    sents = loaders.load_germeval14("test")
    assert sents[0].spans == [Span(start=0, end=2, label="PER")]  # LOCderiv -> O
    assert sents[1].spans == [Span(start=0, end=1, label="LOC")]
    assert {sp.label for s in sents for sp in s.spans} <= set(LABELS_GERMEVAL)
    assert sents[0].id == "germeval14-test-0"


@pytest.mark.unit
def test_load_germeval14_merge_policy(monkeypatch, tmp_path):
    p = _germeval_parquet(tmp_path)
    monkeypatch.setattr(loaders, "_germeval_parquet_path", lambda split: p)
    sents = loaders.load_germeval14("test", subtype_policy="merge")
    assert sents[0].spans == [Span(start=0, end=2, label="PER"), Span(start=3, end=4, label="LOC")]


@pytest.mark.unit
def test_load_by_name_dispatch(monkeypatch):
    called = {}
    monkeypatch.setattr(
        loaders,
        "load_conll2003",
        lambda split, limit=None: called.setdefault("c", (split, limit)) or [],
    )
    monkeypatch.setattr(
        loaders,
        "load_germeval14",
        lambda split, limit=None: called.setdefault("g", (split, limit)) or [],
    )
    loaders.load_by_name("conll2003", "test", limit=5)
    loaders.load_by_name("germeval14", "validation")
    assert called == {"c": ("test", 5), "g": ("validation", None)}
    with pytest.raises(ValueError):
        loaders.load_by_name("unbekannt", "test")
