"""Integrationstest des Analyzers: PDF + Fake-KI -> Korrekturen."""

import json

import pytest
from tests.fixtures.pdf_factory import make_pdf

from korrektor.domain import PageRange
from korrektor.errors import AiError, ErrorCode
from korrektor.services.ai.openai_client import OpenAiClient
from korrektor.services.analysis.analyzer import Analyzer
from korrektor.services.pdf.extractor import PdfDocument
from korrektor.services.pdf.page_mapper import PageMapper


class _ScriptedClient(OpenAiClient):
    """OpenAiClient-Ersatz, der vorgegebene JSON-Antworten je Aufruf liefert."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def complete_json(self, system_prompt, user_prompt):  # noqa: D401
        resp = self._responses[self.calls]
        self.calls += 1
        return resp


@pytest.fixture
def sample_pdf(tmp_path):
    return make_pdf(
        tmp_path / "heft.pdf",
        [
            "Auf dieser Seite steht das Wort Veranstalltung mit Fehler.",
            "Diese Seite ist fehlerfrei.",
        ],
    )


@pytest.mark.integration
def test_analyze_range_collects_and_renumbers(sample_pdf):
    page0 = json.dumps(
        {
            "corrections": [
                {
                    "original_text": "Veranstalltung",
                    "corrected_text": "Veranstaltung",
                    "category": "A",
                    "action_type": "ersetzen durch",
                    "description": "Doppel-l",
                    "reason": "Rechtschreibung",
                }
            ]
        }
    )
    page1 = '{"corrections": []}'
    analyzer = Analyzer(
        client=_ScriptedClient([page0, page1]),
        mapper=PageMapper.from_reference(0, 1),
    )
    with PdfDocument(sample_pdf) as doc:
        results = analyzer.analyze_range(doc, PageRange(start=0, end=1))

    assert len(results) == 1
    c = results[0]
    assert c.id == "K-001"
    assert c.pdf_page == 0
    assert c.printed_page == 1
    # Trefferkoordinaten wurden im echten PDF lokalisiert.
    assert c.location is not None and len(c.location.rects) >= 1


@pytest.mark.integration
def test_ocr_artifact_is_filtered_out(sample_pdf):
    page0 = json.dumps(
        {
            "corrections": [
                {
                    "original_text": "Veranstalltung",
                    "corrected_text": "Veranstaltung",
                    "category": "A",
                    "action_type": "ersetzen durch",
                }
            ]
        }
    )
    # Auf Seite 2 nur ein reines Trennungsartefakt -> muss verschwinden.
    page1 = json.dumps(
        {
            "corrections": [
                {
                    "original_text": "Veroeffentlichungs-kanaele",
                    "corrected_text": "Veroeffentlichungskanaele",
                    "category": "A",
                    "action_type": "ersetzen durch",
                }
            ]
        }
    )
    analyzer = Analyzer(client=_ScriptedClient([page0, page1]))
    with PdfDocument(sample_pdf) as doc:
        results = analyzer.analyze_range(doc, PageRange(start=0, end=1))

    assert len(results) == 1
    assert results[0].original_text == "Veranstalltung"


@pytest.mark.integration
def test_segment_too_large_raises(sample_pdf):
    analyzer = Analyzer(client=_ScriptedClient(["{}"]), max_chars_per_segment=5)
    with PdfDocument(sample_pdf) as doc, pytest.raises(AiError) as exc:
        analyzer.analyze_range(doc, PageRange(start=0, end=0))
    assert exc.value.code is ErrorCode.SEGMENT_TOO_LARGE
