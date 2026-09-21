"""Unit-Tests fuer die BIO <-> Span-Konvertierung."""

import pytest

from promptner.data.bio import bio_to_spans, spans_to_bio
from promptner.domain import Span
from promptner.errors import DataError


@pytest.mark.unit
def test_bio_to_spans_basic():
    tags = ["B-PER", "I-PER", "O", "B-LOC", "O"]
    assert bio_to_spans(tags) == [
        Span(start=0, end=2, label="PER"),
        Span(start=3, end=4, label="LOC"),
    ]


@pytest.mark.unit
def test_bio_to_spans_adjacent_entities():
    tags = ["B-ORG", "B-ORG", "I-ORG"]
    assert bio_to_spans(tags) == [
        Span(start=0, end=1, label="ORG"),
        Span(start=1, end=3, label="ORG"),
    ]


@pytest.mark.unit
def test_lenient_inside_without_begin_starts_span():
    assert bio_to_spans(["O", "I-PER", "I-PER"]) == [Span(start=1, end=3, label="PER")]


@pytest.mark.unit
def test_inside_with_label_change_starts_new_span():
    assert bio_to_spans(["B-PER", "I-LOC"]) == [
        Span(start=0, end=1, label="PER"),
        Span(start=1, end=2, label="LOC"),
    ]


@pytest.mark.unit
def test_invalid_prefix_raises():
    with pytest.raises(DataError):
        bio_to_spans(["X-PER"])


@pytest.mark.unit
def test_roundtrip():
    tags = ["O", "B-MISC", "I-MISC", "I-MISC", "O", "B-PER"]
    assert spans_to_bio(bio_to_spans(tags), len(tags)) == tags


@pytest.mark.unit
def test_spans_to_bio_empty():
    assert spans_to_bio([], 3) == ["O", "O", "O"]
