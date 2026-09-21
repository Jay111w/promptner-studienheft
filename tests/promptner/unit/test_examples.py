"""Unit-Tests fuer den handgeschriebenen Beispielpool."""

import pytest

from promptner.prompting.definitions import resolve_type
from promptner.prompting.examples import EXAMPLE_POOL, select_examples


@pytest.mark.unit
@pytest.mark.parametrize("dataset", ["conll2003", "germeval14"])
def test_pool_size_and_shape(dataset):
    pool = EXAMPLE_POOL[dataset]
    assert len(pool) >= 10
    for ex in pool:
        assert any(c.is_entity for c in ex.candidates), ex.tokens
        assert any(not c.is_entity for c in ex.candidates), ex.tokens
        text = " ".join(ex.tokens)
        for c in ex.candidates:
            assert c.text in text, (c.text, text)
            assert c.explanation, c.text
            if c.is_entity:
                assert resolve_type(dataset, c.type_name) is not None, c.type_name


@pytest.mark.unit
def test_select_examples_deterministic_and_seed_sensitive():
    a = select_examples("conll2003", k=5, seed=1)
    b = select_examples("conll2003", k=5, seed=1)
    c = select_examples("conll2003", k=5, seed=2)
    assert a == b and len(a) == 5
    assert [e.tokens for e in a] != [e.tokens for e in c]
    assert select_examples("conll2003", k=0, seed=1) == []
