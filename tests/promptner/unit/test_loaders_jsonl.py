"""Unit-Tests fuer den JSONL-Loader (eigene Daten)."""

import pytest

from promptner.data.loaders import load_jsonl, save_jsonl
from promptner.domain import Sentence, Span
from promptner.errors import DataError, ErrorCode


@pytest.mark.unit
def test_roundtrip(tmp_path):
    sents = [
        Sentence(
            id="s1", tokens=["Peter", "kam"], spans=[Span(start=0, end=1, label="PER")], source="t"
        ),
        Sentence(id="s2", tokens=["Nichts"], spans=[], source="t"),
    ]
    p = save_jsonl(sents, tmp_path / "x.jsonl")
    assert p.is_file()
    assert load_jsonl(p) == sents


@pytest.mark.unit
def test_missing_file():
    with pytest.raises(DataError) as exc:
        load_jsonl("/nirgends/x.jsonl")
    assert exc.value.code is ErrorCode.DATASET_NOT_FOUND


@pytest.mark.unit
def test_broken_line_reports_line_number(tmp_path):
    p = tmp_path / "b.jsonl"
    p.write_text('{"id":"a","tokens":["x"],"spans":[]}\nnicht json\n', encoding="utf-8")
    with pytest.raises(DataError) as exc:
        load_jsonl(p)
    assert exc.value.code is ErrorCode.DATASET_PARSE_FAILED
    assert exc.value.context["line"] == 2


@pytest.mark.unit
def test_blank_lines_ignored(tmp_path):
    p = tmp_path / "c.jsonl"
    p.write_text('\n{"id":"a","tokens":["x"],"spans":[]}\n\n', encoding="utf-8")
    assert len(load_jsonl(p)) == 1
