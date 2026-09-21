"""Integrationstests fuer den AppController (GUI-unabhaengig)."""

import json

import pytest
from docx import Document
from tests.fixtures.pdf_factory import make_pdf

from korrektor.domain import CorrectionStatus, PageRange
from korrektor.errors import ErrorCode, KorrektorError
from korrektor.services.ai.openai_client import OpenAiClient
from korrektor.services.analysis.analyzer import Analyzer
from korrektor.services.pdf.page_mapper import PageMapper
from korrektor.ui.view_models import AppController

PAGE0 = json.dumps(
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


class _ScriptedClient(OpenAiClient):
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def complete_json(self, system_prompt, user_prompt):
        resp = self._responses[self.calls]
        self.calls += 1
        return resp


@pytest.fixture
def pdf(tmp_path):
    return make_pdf(
        tmp_path / "heft.pdf",
        ["Text mit Veranstalltung als Fehler.", "Zweite Seite ohne Fehler."],
    )


def _analyzer(responses):
    return Analyzer(client=_ScriptedClient(responses), mapper=PageMapper())


@pytest.mark.integration
def test_load_pdf_sets_info(pdf):
    ctrl = AppController()
    info = ctrl.load_pdf(pdf)
    assert info.page_count == 2
    assert ctrl.document_info is not None


@pytest.mark.integration
def test_run_analysis_stores_corrections_and_resets_active(pdf):
    ctrl = AppController()
    ctrl.load_pdf(pdf)
    results = ctrl.run_analysis(
        PageRange(start=0, end=1), analyzer=_analyzer([PAGE0, '{"corrections": []}'])
    )
    assert len(results) == 1
    assert ctrl.corrections[0].id == "K-001"
    assert ctrl.status.analysis_active is False
    assert ctrl.status.has_errors is False


@pytest.mark.integration
def test_run_analysis_without_document_raises():
    ctrl = AppController()
    with pytest.raises(KorrektorError) as exc:
        ctrl.run_analysis(PageRange(start=0, end=0))
    assert exc.value.code is ErrorCode.INVALID_INPUT


@pytest.mark.integration
def test_approve_reject_edit_and_accept(pdf):
    ctrl = AppController()
    ctrl.load_pdf(pdf)
    ctrl.run_analysis(PageRange(start=0, end=1), analyzer=_analyzer([PAGE0, '{"corrections": []}']))
    cid = ctrl.corrections[0].id

    ctrl.reject(cid)
    assert ctrl.accepted_corrections() == []

    ctrl.approve(cid)
    assert len(ctrl.accepted_corrections()) == 1

    ctrl.edit(cid, "Veranstaltung!")
    c = ctrl.corrections[0]
    assert c.status is CorrectionStatus.EDITED
    assert c.corrected_text == "Veranstaltung!"


@pytest.mark.integration
def test_approve_all(pdf):
    ctrl = AppController()
    ctrl.load_pdf(pdf)
    ctrl.run_analysis(PageRange(start=0, end=1), analyzer=_analyzer([PAGE0, '{"corrections": []}']))
    ctrl.approve_all()
    assert all(c.status is CorrectionStatus.APPROVED for c in ctrl.corrections)


@pytest.mark.integration
def test_export_all_writes_three_files(pdf, tmp_path):
    ctrl = AppController()
    ctrl.load_pdf(pdf)
    ctrl.run_analysis(PageRange(start=0, end=1), analyzer=_analyzer([PAGE0, '{"corrections": []}']))
    ctrl.approve_all()
    out = tmp_path / "out"
    result = ctrl.export_all(out)

    assert result.annotated_pdf.is_file()
    assert result.word.is_file()
    assert result.changelog_pdf.is_file()
    # Word enthaelt die freigegebene Korrektur.
    document = Document(result.word)
    assert len(document.tables[0].rows) == 2  # Kopf + 1 Zeile
