"""Unit-Tests fuer den Antwort-Parser."""

import json

import pytest

from korrektor.domain import ActionType, Category
from korrektor.errors import AiError, ErrorCode
from korrektor.services.ai.response_parser import parse_corrections


@pytest.mark.unit
def test_parse_valid_response():
    raw = json.dumps(
        {
            "corrections": [
                {
                    "original_text": "diese Veranstalltung",
                    "corrected_text": "diese Veranstaltung",
                    "category": "A",
                    "action_type": "ersetzen durch",
                    "description": "Doppel-l",
                    "reason": "Rechtschreibung",
                }
            ]
        }
    )
    result = parse_corrections(raw, pdf_page=4, printed_page=2)
    assert len(result) == 1
    c = result[0]
    assert c.id == "K-001"
    assert c.pdf_page == 4
    assert c.printed_page == 2
    assert c.category is Category.A
    assert c.action_type is ActionType.REPLACE
    assert c.location.quote == "diese Veranstalltung"


@pytest.mark.unit
def test_parse_empty_corrections():
    assert parse_corrections('{"corrections": []}', pdf_page=0) == []


@pytest.mark.unit
def test_parse_accepts_bare_list():
    raw = json.dumps(
        [
            {
                "original_text": "x",
                "corrected_text": "",
                "category": "B",
                "action_type": "streichen",
            }
        ]
    )
    result = parse_corrections(raw, pdf_page=1)
    assert result[0].action_type is ActionType.DELETE


@pytest.mark.unit
def test_parse_start_index_offsets_ids():
    raw = '{"corrections": [{"original_text": "a", "category": "A", "action_type": "streichen"}]}'
    result = parse_corrections(raw, pdf_page=0, start_index=5)
    assert result[0].id == "K-005"


@pytest.mark.unit
def test_invalid_json_raises():
    with pytest.raises(AiError) as exc:
        parse_corrections("nicht json", pdf_page=0)
    assert exc.value.code is ErrorCode.AI_RESPONSE_INVALID


@pytest.mark.unit
def test_unknown_category_raises():
    raw = '{"corrections": [{"original_text": "a", "category": "Z", "action_type": "streichen"}]}'
    with pytest.raises(AiError) as exc:
        parse_corrections(raw, pdf_page=0)
    assert exc.value.code is ErrorCode.AI_RESPONSE_INVALID


@pytest.mark.unit
def test_unknown_action_raises():
    raw = '{"corrections": [{"original_text": "a", "category": "A", "action_type": "loeschen"}]}'
    with pytest.raises(AiError):
        parse_corrections(raw, pdf_page=0)
