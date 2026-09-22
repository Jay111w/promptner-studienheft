"""Unit-Tests fuer die BERT-Baseline (reine Funktionen, kein Modell, kein torch noetig)."""

import pytest

from promptner.baseline.bert import (
    LABELS_CONLL_BIO,
    align_labels,
    first_subword_predictions,
    label_ids_to_bio,
)
from promptner.data.bio import bio_to_spans, spans_to_bio
from promptner.domain import Span


@pytest.mark.unit
def test_align_labels_first_subword_only():
    # Woerter: ["Chris", "Lewis", "played"] -> WordPiece: [CLS] Chris Lew ##is play ##ed [SEP]
    word_ids = [None, 0, 1, 1, 2, 2, None]
    labels = [1, 2, 0]  # B-PER, I-PER, O
    assert align_labels(word_ids, labels) == [-100, 1, 2, -100, 0, -100, -100]


@pytest.mark.unit
def test_first_subword_predictions_one_per_word():
    word_ids = [None, 0, 1, 1, 2, 2, None]
    pred_ids = [0, 1, 2, 5, 0, 3, 0]  # das 2. Subword von "Lewis" sagt 5, zaehlt nicht
    assert first_subword_predictions(word_ids, pred_ids, n_words=3) == [1, 2, 0]


@pytest.mark.unit
def test_bio_label_roundtrip_through_ids():
    spans = [Span(start=1, end=3, label="PER"), Span(start=4, end=5, label="LOC")]
    tags = spans_to_bio(spans, 6)
    ids = [LABELS_CONLL_BIO.index(t) for t in tags]
    assert label_ids_to_bio(ids) == tags
    assert bio_to_spans(label_ids_to_bio(ids)) == spans


@pytest.mark.unit
def test_label_set_is_bio_over_conll_types():
    assert LABELS_CONLL_BIO[0] == "O"
    assert {t[2:] for t in LABELS_CONLL_BIO if t != "O"} == {"PER", "ORG", "LOC", "MISC"}
    assert len(LABELS_CONLL_BIO) == 9
