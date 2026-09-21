"""Unit-Tests fuer PromptConfig, Candidate, Prediction."""

import pytest
from pydantic import ValidationError

from promptner.domain import Candidate, Prediction, PromptConfig, Span


@pytest.mark.unit
def test_default_config_is_full_promptner():
    c = PromptConfig(dataset="conll2003")
    assert c.use_definition and c.use_cot and c.use_candidates
    assert c.k_examples == 5 and c.output_format == "text" and c.seed == 1
    assert c.short_name() == "conll2003_def1_k5_cot1_cand1_text_s1"


@pytest.mark.unit
def test_short_name_reflects_flags():
    c = PromptConfig(
        dataset="germeval14",
        use_definition=False,
        k_examples=0,
        use_cot=False,
        use_candidates=False,
        output_format="json",
        seed=3,
    )
    assert c.short_name() == "germeval14_def0_k0_cot0_cand0_json_s3"


@pytest.mark.unit
def test_k_examples_restricted():
    with pytest.raises(ValidationError):
        PromptConfig(dataset="conll2003", k_examples=7)


@pytest.mark.unit
def test_candidate_and_prediction_defaults():
    cand = Candidate(text="Ohio", is_entity=True, explanation="a state", type_name="location")
    p = Prediction(
        sentence_id="x", spans=[Span(start=0, end=1, label="LOC")], candidates=[cand], raw="..."
    )
    assert p.parse_ok is True and p.retries == 0 and p.n_unmatched == 0 and p.n_unknown_type == 0
