"""Unit-Tests fuer die Annotator-Uebereinstimmung (Studienheft-Sample)."""

import pytest

from promptner.domain import Sentence, Span
from promptner.errors import DataError
from promptner.eval.agreement import cohen_kappa, compare, render_markdown


def sent(sid: str, tokens: list[str], spans: list[tuple[int, int, str]]) -> Sentence:
    return Sentence(
        id=sid,
        tokens=tokens,
        spans=[Span(start=s, end=e, label=lbl) for s, e, lbl in spans],
        source="studienheft",
    )


TOKENS = ["Die", "EU", "sitzt", "in", "Brüssel", "."]


@pytest.mark.unit
def test_cohen_kappa_identical_is_one():
    tags = ["O", "B-PER", "I-PER", "O"]
    assert cohen_kappa(tags, tags) == 1.0


@pytest.mark.unit
def test_cohen_kappa_all_one_category_is_one():
    """Beide markieren nichts: po = 1. Die Formel waere 0/0, das Ergebnis ist Einigkeit."""
    assert cohen_kappa(["O", "O", "O"], ["O", "O", "O"]) == 1.0


@pytest.mark.unit
def test_cohen_kappa_known_value():
    # po = 3/4; pe = (3/4)(2/4) + (1/4)(1/4) = 7/16; kappa = (0,75 - 0,4375) / 0,5625
    a = ["O", "B-PER", "O", "O"]
    b = ["O", "B-PER", "B-LOC", "O"]
    assert cohen_kappa(a, b) == pytest.approx(0.5555, abs=1e-4)


@pytest.mark.unit
def test_cohen_kappa_rejects_different_lengths():
    with pytest.raises(DataError):
        cohen_kappa(["O"], ["O", "O"])


@pytest.mark.unit
def test_identical_annotation_is_perfect_agreement():
    a = [sent("s-0", TOKENS, [(1, 2, "ORG"), (4, 5, "LOC")])]
    rep = compare(a, [s.model_copy(deep=True) for s in a])
    assert rep.span_f1 == 1.0
    assert rep.token_kappa == 1.0
    assert rep.disagreements == []
    assert rep.n_spans_a == rep.n_spans_b == 2


@pytest.mark.unit
def test_type_disagreement_is_counted_on_both_sides():
    """Gleiche Grenzen, anderer Typ: zaehlt fuer keinen der beiden als Treffer."""
    a = [sent("s-0", TOKENS, [(1, 2, "ORG")])]
    b = [sent("s-0", TOKENS, [(1, 2, "LOC")])]
    rep = compare(a, b)
    assert rep.span_f1 == 0.0
    assert len(rep.disagreements) == 1
    d = rep.disagreements[0]
    assert [s.label for s in d.only_a] == ["ORG"]
    assert [s.label for s in d.only_b] == ["LOC"]


@pytest.mark.unit
def test_boundary_disagreement_halves_the_f1():
    """Einer markiert ein Token mehr; ein Span stimmt, einer nicht -> F1 = 0,5."""
    a = [sent("s-0", TOKENS, [(0, 2, "ORG"), (4, 5, "LOC")])]
    b = [sent("s-0", TOKENS, [(1, 2, "ORG"), (4, 5, "LOC")])]
    rep = compare(a, b)
    assert rep.span_f1 == pytest.approx(0.5)


@pytest.mark.unit
def test_only_common_sentences_are_compared():
    a = [sent("s-0", TOKENS, [(1, 2, "ORG")]), sent("s-1", TOKENS, [])]
    b = [sent("s-0", TOKENS, [(1, 2, "ORG")]), sent("s-9", TOKENS, [])]
    rep = compare(a, b)
    assert rep.n_sentences == 1
    assert rep.span_f1 == 1.0


@pytest.mark.unit
def test_no_common_sentences_is_an_error():
    a = [sent("s-0", TOKENS, [])]
    b = [sent("s-9", TOKENS, [])]
    with pytest.raises(DataError, match="gemeinsam"):
        compare(a, b)


@pytest.mark.unit
def test_differing_tokens_for_the_same_id_is_an_error():
    """Beide muessen dieselbe Vorlage annotiert haben, sonst vergleicht man Aepfel mit Birnen."""
    a = [sent("s-0", TOKENS, [])]
    b = [sent("s-0", ["Ein", "anderer", "Satz"], [])]
    with pytest.raises(DataError, match="s-0"):
        compare(a, b)


@pytest.mark.unit
def test_unknown_labels_are_reported():
    a = [sent("s-0", TOKENS, [(1, 2, "FIRMA")])]
    b = [sent("s-0", TOKENS, [(1, 2, "ORG")])]
    rep = compare(a, b)
    assert rep.unknown_labels == {"FIRMA"}


@pytest.mark.unit
def test_markdown_names_the_numbers_and_the_disagreement():
    a = [sent("s-0", TOKENS, [(1, 2, "ORG")])]
    b = [sent("s-0", TOKENS, [(1, 2, "LOC")])]
    text = render_markdown(compare(a, b))
    assert "s-0" in text
    assert "ORG" in text and "LOC" in text
    assert "Kappa" in text
