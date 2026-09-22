"""Unit-Tests fuer den PromptNER-Prompt-Builder (Figure 1 des Papers)."""

import pytest

from promptner.domain import PromptConfig, Sentence
from promptner.prompting.builder import build_prompt, format_answer, prompt_hash
from promptner.prompting.examples import select_examples

SENT = Sentence(id="t", tokens=["Ohio", "is", "a", "state", "."])


def _user(**kw) -> str:
    """Gesamter Prompt-Text ueber alle Turns (Defn, Q, Beispiele, Zielsatz)."""
    return build_prompt(PromptConfig(dataset="conll2003", **kw), SENT).full_text


@pytest.mark.unit
def test_examples_become_separate_chat_turns():
    # Chat-Modelle beantworten sonst die Beispiele erneut (Echo); jedes Beispiel wird
    # daher als eigenes User/Assistant-Paar gesendet, der Zielsatz als letzter User-Turn.
    req = build_prompt(PromptConfig(dataset="conll2003"), SENT)
    assert len(req.turns) == 5
    assert req.turns[0][0].startswith("Defn: ")
    assert "Q: Given the paragraph below" in req.turns[0][0]
    for user, assistant in req.turns:
        assert user.rstrip().endswith("Answer:")
        assert assistant.startswith("1. ")
    assert req.user == "Paragraph: Ohio is a state .\n\nAnswer:"
    assert "Defn:" not in req.user and "| True" not in req.user


@pytest.mark.unit
def test_zero_shot_has_no_turns_and_preamble_in_user():
    req = build_prompt(PromptConfig(dataset="conll2003", k_examples=0), SENT)
    assert req.turns == ()
    assert req.user.startswith("Defn: ")
    assert req.user.rstrip().endswith("Paragraph: Ohio is a state .\n\nAnswer:")


@pytest.mark.unit
def test_full_prompt_structure():
    req = build_prompt(PromptConfig(dataset="conll2003"), SENT)
    u = req.full_text
    assert req.turns[0][0].startswith("Defn: ")  # erste User-Nachricht beginnt mit Defn
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
    assert "Defn: Eine Entität" in de.full_text
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
