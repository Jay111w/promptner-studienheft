"""Unit-Tests fuer die Domain-Modelle Span und Sentence."""

import pytest

from promptner.domain import LABELS_CONLL, LABELS_GERMEVAL, Sentence, Span
from promptner.errors import DataError, ErrorCode


@pytest.mark.unit
def test_span_text_from_tokens():
    s = Span(start=1, end=3, label="PER")
    assert s.text(["Herr", "Peter", "Blackburn", "kam"]) == "Peter Blackburn"


@pytest.mark.unit
def test_sentence_text_and_bio_tags():
    s = Sentence(
        id="x", tokens=["Peter", "Blackburn", "kam"], spans=[Span(start=0, end=2, label="PER")]
    )
    assert s.text == "Peter Blackburn kam"
    assert s.bio_tags() == ["B-PER", "I-PER", "O"]


@pytest.mark.unit
def test_overlapping_spans_rejected():
    with pytest.raises(DataError) as exc:
        Sentence(
            id="x",
            tokens=["a", "b", "c"],
            spans=[Span(start=0, end=2, label="PER"), Span(start=1, end=3, label="LOC")],
        )
    assert exc.value.code is ErrorCode.INVALID_BIO_SEQUENCE


@pytest.mark.unit
def test_span_out_of_range_rejected():
    with pytest.raises(DataError):
        Sentence(id="x", tokens=["a", "b"], spans=[Span(start=1, end=3, label="PER")])


@pytest.mark.unit
def test_spans_sorted_on_construction():
    s = Sentence(
        id="x",
        tokens=["a", "b", "c", "d"],
        spans=[Span(start=2, end=3, label="LOC"), Span(start=0, end=1, label="PER")],
    )
    assert [sp.start for sp in s.spans] == [0, 2]


@pytest.mark.unit
def test_label_sets():
    assert LABELS_CONLL == ("PER", "ORG", "LOC", "MISC")
    assert LABELS_GERMEVAL == ("PER", "ORG", "LOC", "OTH")
