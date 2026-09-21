"""Unit-Tests fuer die seqeval-basierte Evaluation."""

import pytest

from promptner.domain import Sentence, Span
from promptner.errors import DataError, ErrorCode
from promptner.eval import EvalResult, evaluate


def _gold():
    return [
        Sentence(
            id="a",
            tokens=["Peter", "Blackburn", "in", "Berlin"],
            spans=[Span(start=0, end=2, label="PER"), Span(start=3, end=4, label="LOC")],
        ),
        Sentence(id="b", tokens=["EU", "rejects"], spans=[Span(start=0, end=1, label="ORG")]),
    ]


@pytest.mark.unit
def test_perfect_prediction():
    gold = _gold()
    res = evaluate(gold, [s.spans for s in gold])
    assert isinstance(res, EvalResult)
    assert res.precision == res.recall == res.f1 == 1.0
    assert res.n_sentences == 2
    assert res.per_type["PER"].support == 1
    assert res.per_type["LOC"].support == 1
    assert res.per_type["ORG"].support == 1


@pytest.mark.unit
def test_empty_prediction_is_zero():
    res = evaluate(_gold(), [[], []])
    assert res.precision == 0.0 and res.recall == 0.0 and res.f1 == 0.0


@pytest.mark.unit
def test_boundary_error_counts_as_fp_and_fn():
    gold = _gold()
    pred = [
        [Span(start=0, end=1, label="PER"), Span(start=3, end=4, label="LOC")],
        [Span(start=0, end=1, label="ORG")],
    ]
    res = evaluate(gold, pred)
    # 2 von 3 korrekt, 1 FP, 1 FN -> P = R = F1 = 2/3
    assert round(res.f1, 4) == round(2 / 3, 4)
    assert res.per_type["PER"].f1 == 0.0


@pytest.mark.unit
def test_length_mismatch_raises():
    with pytest.raises(DataError) as exc:
        evaluate(_gold(), [[]])
    assert exc.value.code is ErrorCode.EVAL_FAILED
