"""Unit-Tests fuer die maschinelle Durchsetzung der Annotationsrichtlinien.

Die Faelle sind keine erfundenen Beispiele, sondern Spans, die in
``data/studienheft/gold_*.jsonl`` tatsaechlich so annotiert waren.
"""

import pytest

from promptner.data.normalize import (
    ist_eigenname,
    normalisiere_satz,
    normalisiere_span,
    ohne_ueberlappung,
)
from promptner.domain import Sentence, Span


def _norm(tokens: list[str], start: int, end: int, label: str = "OTH") -> Span | None:
    return normalisiere_span(tokens, Span(start=start, end=end, label=label))


@pytest.mark.unit
def test_gattungsbegriff_faellt_weg():
    """ANNOTATION.md: "Nur Eigennamen, keine Gattungsbegriffe"."""
    assert _norm(["die", "Vision", "eruiert"], 1, 2) is None
    assert _norm(["der", "Bund", "handelt"], 1, 2, "ORG") is None
    assert _norm(["das", "Gesetz", "gilt"], 1, 2) is None


@pytest.mark.unit
def test_rollenbezeichnung_ist_keine_person():
    """ANNOTATION.md zu PER: "nicht: die Bundeskanzlerin"."""
    assert _norm(["von", "Bürgerinnen", "und", "Bürgern"], 1, 2, "PER") is None


@pytest.mark.unit
def test_modifikator_wird_abgeschnitten():
    """Ein vorangestelltes Adjektiv gehoert nicht zum Namen - und was bleibt, ist hier generisch."""
    tokens = ["die", "rechtlichen", "Grundlagen", "sind"]
    assert _norm(tokens, 1, 3) is None  # getrimmt zu "Grundlagen", dann Gattungsbegriff

    tokens = ["das", "elektronische", "Elster-Zertifikat", "gilt"]
    span = _norm(tokens, 1, 3)
    assert span == Span(start=2, end=3, label="OTH")


@pytest.mark.unit
def test_nachgestellte_abkuerzung_in_klammern_faellt_ab():
    tokens = ["das", "E-Government-Gesetz", "Rheinland-Pfalz", "(", "EGovGRP", ")", "regelt"]
    assert _norm(tokens, 1, 6) == Span(start=1, end=3, label="OTH")


@pytest.mark.unit
def test_jahreszahl_bleibt_teil_des_programmnamens():
    """Wie das Beispiel "Olympische Spiele 2024" in ANNOTATION.md."""
    tokens = ["die", "Digitale", "Dekade", "2030", "wurde"]
    assert _norm(tokens, 1, 4) == Span(start=1, end=4, label="OTH")


@pytest.mark.unit
def test_fundstelle_wird_auf_den_gesetzesnamen_reduziert():
    tokens = ["gemäß", "§", "2", "Absatz", "1", "OZG", "sind"]
    assert _norm(tokens, 1, 6) == Span(start=5, end=6, label="OTH")


@pytest.mark.unit
def test_fundstelle_ohne_namen_faellt_weg():
    tokens = ["auf", "Artikel", "91c", "V", "hinzuweisen"]
    assert _norm(tokens, 1, 4) is None


@pytest.mark.unit
def test_typ_kommt_aus_dem_lexikon_nicht_vom_annotator():
    """ "Bundes" als LOC war ein Fehler; Laender sind LOC, Behoerden ORG, Gesetze OTH."""
    assert ist_eigenname("Rheinland-Pfalz") == "LOC"
    assert ist_eigenname("Bundesministerium des Innern") == "ORG"
    assert ist_eigenname("Onlinezugangsgesetz") == "OTH"
    assert ist_eigenname("OZG") == "OTH"


@pytest.mark.unit
def test_abkuerzung_wird_erkannt_konzept_nicht():
    assert ist_eigenname("OZGÄndG") == "OTH"
    assert ist_eigenname("DeutschlandID") == "OTH"
    assert ist_eigenname("E-Government") is None
    assert ist_eigenname("Ende-zu-Ende-Digitalisierung") is None


@pytest.mark.unit
def test_satz_behaelt_reihenfolge_und_korrigiert_typ():
    satz = Sentence(
        id="s1",
        tokens=["Das", "E-Government-Gesetz", "des", "Bundes", "gilt", "in", "Deutschland", "."],
        spans=[Span(start=6, end=7, label="ORG"), Span(start=1, end=4, label="OTH")],
        source="studienheft",
    )
    neu = normalisiere_satz(satz)
    assert neu.spans == [
        Span(start=1, end=4, label="OTH"),
        Span(start=6, end=7, label="LOC"),  # Lexikon korrigiert ORG zu LOC
    ]


@pytest.mark.unit
def test_zusammenfuehren_zweier_lesarten_nimmt_die_laengere():
    """Beim Vereinen des gemeinsamen Blocks koennen sich zwei Lesarten ueberlappen."""
    a = [Span(start=1, end=2, label="OTH"), Span(start=6, end=7, label="LOC")]
    b = [Span(start=1, end=4, label="OTH")]
    assert ohne_ueberlappung(a + b) == [
        Span(start=1, end=4, label="OTH"),
        Span(start=6, end=7, label="LOC"),
    ]
