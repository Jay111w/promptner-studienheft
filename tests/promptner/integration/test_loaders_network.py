"""Laedt echte Datensaetze (Netz noetig). In CI uebersprungen."""

import pytest

from promptner.data.loaders import load_by_name
from promptner.domain import LABELS_CONLL, LABELS_GERMEVAL

pytestmark = pytest.mark.network


@pytest.mark.parametrize(
    ("name", "labels"), [("conll2003", LABELS_CONLL), ("germeval14", LABELS_GERMEVAL)]
)
def test_real_datasets_load_five_sentences(name, labels):
    sents = load_by_name(name, "validation", limit=5)
    assert len(sents) == 5
    assert all(len(s.tokens) > 0 for s in sents)
    assert {sp.label for s in sents for sp in s.spans} <= set(labels)
