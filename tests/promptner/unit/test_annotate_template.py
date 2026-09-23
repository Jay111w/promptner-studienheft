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


@pytest.mark.unit
def test_strip_repeated_lines_removes_running_heads():
    """Kopf- und Fusszeilen eines Studienhefts stehen auf jeder Seite und zerschneiden Saetze."""
    from promptner.data.segment import strip_repeated_lines

    seiten = [
        "Grundlagen des E-Governments 9\nDie Behoerde entscheidet.\nVOP01A",
        "Grundlagen des E-Governments 10\nDas Land setzt es um.\nVOP01A",
        "Grundlagen des E-Governments 11\nDer Bund folgt spaeter.\nVOP01A",
    ]
    out = strip_repeated_lines(seiten)
    assert "Grundlagen des E-Governments" not in out
    assert "VOP01A" not in out
    assert "Die Behoerde entscheidet." in out
    assert "Der Bund folgt spaeter." in out


@pytest.mark.unit
def test_strip_repeated_lines_keeps_content_that_merely_repeats_twice():
    """Ein Satz, der zweimal vorkommt, ist noch keine Kopfzeile."""
    from promptner.data.segment import strip_repeated_lines

    seiten = ["Der Bund handelt.", "Der Bund handelt.", "Etwas anderes."]
    out = strip_repeated_lines(seiten)
    assert out.count("Der Bund handelt.") == 2


@pytest.mark.unit
def test_strip_repeated_lines_drops_page_numbers_and_short_noise():
    from promptner.data.segment import strip_repeated_lines

    seiten = ["17\nEin vollstaendiger Satz steht hier.\n- 3 -", "18\nUnd noch einer.\n- 4 -"]
    out = strip_repeated_lines(seiten)
    assert "17" not in out.split()
    assert "Ein vollstaendiger Satz steht hier." in out


@pytest.mark.unit
def test_strip_repeated_lines_repairs_hyphenation_across_the_removed_head():
    """Aus 'Aus-' + Kopfzeile + 'gangssituation' muss wieder ein Wort werden."""
    from promptner.data.segment import strip_repeated_lines

    seiten = [
        "Zuerst wird die Aus-\nGrundlagen des E-Governments 9\ngangssituation beschrieben.",
        "Grundlagen des E-Governments 10\nDanach folgt der Rest.",
        "Grundlagen des E-Governments 11\nUnd zuletzt das Fazit.",
    ]
    out = strip_repeated_lines(seiten)
    assert "Ausgangssituation beschrieben." in out
