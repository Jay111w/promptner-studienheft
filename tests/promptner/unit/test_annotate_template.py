"""Unit-Tests fuer die Satz-/Token-Aufbereitung der Annotations-Vorlage."""

import pytest

from promptner.data.segment import segment_text


@pytest.mark.unit
def test_segment_splits_sentences_and_tokens():
    text = "Peter Blackburn kam nach Berlin. Er arbeitete bei der EU!"
    sents = segment_text(text, source="test")
    assert [s.tokens for s in sents] == [
        ["Peter", "Blackburn", "kam", "nach", "Berlin", "."],
        ["Er", "arbeitete", "bei", "der", "EU", "!"],
    ]
    assert sents[0].id == "test-0" and sents[1].id == "test-1"
    assert all(s.spans == [] for s in sents)


@pytest.mark.unit
def test_segment_handles_hyphenation_and_short_fragments():
    text = "Veröffentlichungs-\nkanäle sind wichtig. Ok. Ende"
    sents = segment_text(text, source="t", min_tokens=3)
    assert sents[0].tokens[0] == "Veröffentlichungskanäle"
    # "Ok." hat nur 2 Tokens und faellt raus; "Ende" ebenfalls
    assert len(sents) == 1
