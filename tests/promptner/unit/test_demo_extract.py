"""Unit-Tests fuer die Demo-Extraktion (Fake-Client, kein PDF, kein Qt)."""

import pytest

from promptner.demo import extract_entities
from promptner.llm.client import LlmClient


class _FakeClient(LlmClient):
    def __init__(self):
        self.calls_made = 0

    def complete(self, request):
        self.calls_made += 1
        # Antwort im deutschen Paper-Format: Text | True/False | Begruendung (Typ)
        return (
            "1. Wolf Peter Bree | True | Name einer Person (Person)\n"
            "2. Universität Hildesheim | True | eine Hochschule (Organisation)\n"
            "3. Firmengründer | False | Rollenbezeichnung"
        )


@pytest.mark.unit
def test_extract_entities_maps_hits_to_pages_and_sentences():
    pages = [
        (3, "Firmengründer Wolf Peter Bree arbeitete lange in Berlin."),
        (4, "Er wechselte an die Universität Hildesheim."),
    ]
    ticks: list[tuple[int, int]] = []
    hits = extract_entities(
        pages, _FakeClient(), workers=1, on_progress=lambda d, t: ticks.append((d, t))
    )
    assert [(h.pdf_page, h.text, h.label) for h in hits] == [
        (3, "Wolf Peter Bree", "PER"),
        (4, "Universität Hildesheim", "ORG"),
    ]
    assert hits[0].sentence.startswith("Firmengründer")
    assert ticks == [(1, 2), (2, 2)]


@pytest.mark.unit
def test_extract_entities_empty_pages():
    assert extract_entities([(0, "   "), (1, "zu kurz")], _FakeClient()) == []
