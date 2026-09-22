"""Unit-Tests fuer Antwort-Parser und Span-Alignment."""

import json

import pytest

from promptner.domain import Candidate, PromptConfig, Sentence, Span
from promptner.errors import ErrorCode, ParseError
from promptner.llm.parser import align, parse_answer

FIG1 = """Answer:
1. U.S. Air Force Institute of Technology | True | as he attended this institute is likely a university (university)
2. bachelor 's degree | False | as it is not a university, award or any other entity type
3. aeromechanics | True | as it is a scientific discipline (discipline)
4. Edwards Air Force Base | True | as an Air Force Base is an organised unit (organisation)
5. California | True | as in this case California refers to the state of California itself (location)
6. Wright-Patterson Air Force Base | True | as an Air Force Base is an organisation (organisation)
7. Ohio | True | as it is a state (location)
"""
CFG = PromptConfig(dataset="conll2003")


@pytest.mark.unit
def test_parse_figure1_answer():
    cands = parse_answer(FIG1, CFG)
    assert len(cands) == 7
    assert cands[0] == Candidate(
        text="U.S. Air Force Institute of Technology",
        is_entity=True,
        explanation="as he attended this institute is likely a university",
        type_name="university",
    )
    assert cands[1].is_entity is False and cands[1].type_name is None
    assert cands[6].type_name == "location"


@pytest.mark.unit
def test_parse_without_cot_format():
    cands = parse_answer(
        "1. Ohio | True (location)\n2. state | False\n",
        PromptConfig(dataset="conll2003", use_cot=False),
    )
    assert cands[0] == Candidate(text="Ohio", is_entity=True, explanation="", type_name="location")
    assert cands[1].is_entity is False


@pytest.mark.unit
def test_parse_tolerates_markdown_and_blank_lines():
    raw = "Sure! Here is the answer:\n\n**1.** Ohio | True | a state (location)\n\n- 2. is | False | a verb\n"
    cands = parse_answer(raw, CFG)
    assert [c.text for c in cands] == ["Ohio", "is"]


@pytest.mark.unit
def test_parse_empty_answer_means_no_entities():
    assert parse_answer("Answer:\nNone\n", CFG) == []


@pytest.mark.unit
def test_parse_garbage_raises():
    with pytest.raises(ParseError) as exc:
        parse_answer("I cannot help with that.", CFG)
    assert exc.value.code is ErrorCode.RESPONSE_INVALID


@pytest.mark.unit
def test_parse_json_format():
    raw = json.dumps(
        {
            "candidates": [
                {
                    "text": "Ohio",
                    "is_entity": True,
                    "explanation": "a state",
                    "type_name": "location",
                },
                {"text": "is", "is_entity": False},
            ]
        }
    )
    cands = parse_answer(raw, PromptConfig(dataset="conll2003", output_format="json"))
    assert cands[0].type_name == "location" and cands[1].is_entity is False


@pytest.mark.unit
def test_parse_json_invalid_raises():
    with pytest.raises(ParseError):
        parse_answer(
            '{"candidates": [{"text": 5}]}', PromptConfig(dataset="conll2003", output_format="json")
        )


SENT = Sentence(
    id="s",
    tokens=[
        "He",
        "trained",
        "at",
        "Edwards",
        "Air",
        "Force",
        "Base",
        "in",
        "California",
        "and",
        "again",
        "in",
        "California",
        ".",
    ],
)


@pytest.mark.unit
def test_align_maps_text_to_token_spans_and_labels():
    cands = [
        Candidate(text="Edwards Air Force Base", is_entity=True, type_name="organisation"),
        Candidate(text="California", is_entity=True, type_name="location"),
        Candidate(text="trained", is_entity=False),
    ]
    spans, unmatched, unknown = align(SENT, cands, "conll2003")
    assert spans == [
        Span(start=3, end=7, label="ORG"),
        Span(start=8, end=9, label="LOC"),
        Span(start=12, end=13, label="LOC"),
    ]
    assert unmatched == 0 and unknown == 0


@pytest.mark.unit
def test_align_counts_hallucinations_and_unknown_types():
    cands = [
        Candidate(text="Nevada", is_entity=True, type_name="location"),
        Candidate(text="California", is_entity=True, type_name="galaxy"),
    ]
    spans, unmatched, unknown = align(SENT, cands, "conll2003")
    assert spans == [] and unmatched == 1 and unknown == 1


@pytest.mark.unit
def test_align_overlap_longest_wins_and_case_insensitive_fallback():
    cands = [
        Candidate(text="Air Force Base", is_entity=True, type_name="organisation"),
        Candidate(text="edwards air force base", is_entity=True, type_name="organisation"),
    ]
    spans, unmatched, unknown = align(SENT, cands, "conll2003")
    assert spans == [Span(start=3, end=7, label="ORG")]
    assert unmatched == 0


@pytest.mark.unit
def test_align_handles_punctuation_attached():
    s = Sentence(id="p", tokens=["Berlin", ",", "Germany", "."])
    cands = [
        Candidate(text="Berlin,", is_entity=True, type_name="location"),
        Candidate(text="Germany.", is_entity=True, type_name="location"),
    ]
    spans, unmatched, _ = align(s, cands, "conll2003")
    assert spans == [Span(start=0, end=1, label="LOC"), Span(start=2, end=3, label="LOC")]


@pytest.mark.unit
def test_align_finds_all_case_variants_but_not_lowercase_words():
    # Kandidat aus Ueberschrift ("LEICESTERSHIRE") muss auch "Leicestershire" im Text treffen;
    # "Such" (Nachname) darf aber nicht das Wort "such" matchen.
    sent = Sentence(
        id="p",
        tokens=[
            "LEICESTERSHIRE",
            "won",
            ".",
            "Leicestershire",
            "and",
            "Such",
            "played",
            "such",
            "games",
        ],
    )
    cands = [
        Candidate(text="LEICESTERSHIRE", is_entity=True, type_name="organisation"),
        Candidate(text="Such", is_entity=True, type_name="person"),
    ]
    spans, unmatched, _ = align(sent, cands, "conll2003")
    assert [(s.start, s.end, s.label) for s in spans] == [
        (0, 1, "ORG"),
        (3, 4, "ORG"),
        (5, 6, "PER"),
    ]
    assert unmatched == 0
