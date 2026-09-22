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


@pytest.mark.parametrize("name", ["conll2003", "germeval14"])
def test_fewshot_pool_is_disjoint_from_validation_and_test(name):
    """Kein Pool-Beispiel darf aus Val/Test stammen (sonst Leakage in die Messung)."""
    from promptner.prompting.examples import EXAMPLE_POOL

    n = 5

    def grams(tokens):
        t = [x.lower() for x in tokens]
        return {tuple(t[i : i + n]) for i in range(len(t) - n + 1)}

    for split in ("validation", "test"):
        seen: set[tuple[str, ...]] = set()
        for s in load_by_name(name, split, limit=None):
            seen |= grams(s.tokens)
        for ex in EXAMPLE_POOL[name]:
            assert not (grams(ex.tokens) & seen), (split, " ".join(ex.tokens))
