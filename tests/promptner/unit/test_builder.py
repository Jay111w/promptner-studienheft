"""Unit-Tests fuer den PromptNER-Prompt-Builder (Figure 1 des Papers)."""

import pytest

from promptner.domain import PromptConfig, Sentence
from promptner.prompting.builder import build_prompt, format_answer, prompt_hash
from promptner.prompting.examples import select_examples

SENT = Sentence(id="t", tokens=["Ohio", "is", "a", "state", "."])


def _user(**kw) -> str:
    return build_prompt(PromptConfig(dataset="conll2003", **kw), SENT).user


@pytest.mark.unit
def test_full_prompt_structure():
    u = _user()
    assert u.startswith("Defn: ")
    assert "Q: Given the paragraph below" in u
    assert u.count("Paragraph: ") == 6  # 5 Beispiele + Zielsatz
    assert u.rstrip().endswith("Paragraph: Ohio is a state .\n\nAnswer:")
    assert " | True | " in u and " | False | " in u


@pytest.mark.unit
def test_without_definition():
    assert "Defn:" not in _user(use_definition=False)


@pytest.mark.unit
def test_without_examples():
    u = _user(k_examples=0)
    assert u.count("Paragraph: ") == 1 and "| True" not in u


@pytest.mark.unit
def test_without_cot_has_no_explanations():
    u = _user(use_cot=False)
    assert " | True | " not in u and " | False | " not in u
    assert " | True (" in u


@pytest.mark.unit
def test_without_candidates_lists_only_entities():
    u = _user(use_candidates=False)
    assert "| False" not in u and "| True" in u
    assert "possible entities" not in u  # Frage verlangt nur Entitaeten


@pytest.mark.unit
def test_json_format_instructs_schema():
    u = _user(output_format="json")
    assert '"candidates"' in u and '"is_entity"' in u
    assert "Answer:" in u


@pytest.mark.unit
def test_system_prompt_and_language():
    de = build_prompt(PromptConfig(dataset="germeval14"), SENT)
    assert "Defn: Eine Entität" in de.user
    assert "Absatz:" in de.user and "Antwort:" in de.user
    assert de.system


@pytest.mark.unit
def test_format_answer_roundtrip_shape():
    ex = select_examples("conll2003", k=1, seed=1)[0]
    text = format_answer(list(ex.candidates), PromptConfig(dataset="conll2003"))
    assert text.splitlines()[0].startswith("1. ")
    assert all(" | " in line for line in text.splitlines())


@pytest.mark.unit
def test_prompt_hash_stable_and_flag_sensitive():
    base = PromptConfig(dataset="conll2003")
    assert prompt_hash(base) == prompt_hash(PromptConfig(dataset="conll2003"))
    for kw in (
        {"use_definition": False},
        {"k_examples": 2},
        {"use_cot": False},
        {"use_candidates": False},
        {"output_format": "json"},
        {"seed": 2},
    ):
        assert prompt_hash(PromptConfig(dataset="conll2003", **kw)) != prompt_hash(base), kw
    assert len(prompt_hash(base)) == 12
