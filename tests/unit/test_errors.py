"""Unit-Tests fuer Fehlercodes und Exceptions."""

import pytest

from korrektor.errors import ConfigError, ErrorCode, KorrektorError, PdfError


@pytest.mark.unit
def test_error_code_has_description():
    assert ErrorCode.MISSING_API_KEY.value == "KOR-CFG-001"
    assert "API-Key" in ErrorCode.MISSING_API_KEY.description


@pytest.mark.unit
def test_exception_uses_code_description_by_default():
    err = ConfigError(ErrorCode.MISSING_API_KEY)
    assert err.code is ErrorCode.MISSING_API_KEY
    assert "KOR-CFG-001" in str(err)


@pytest.mark.unit
def test_exception_custom_message_and_context():
    err = PdfError(
        ErrorCode.PDF_NOT_FOUND,
        "Datei fehlt",
        context={"path": "heft.pdf"},
    )
    assert err.message == "Datei fehlt"
    assert err.context["path"] == "heft.pdf"
    assert err.to_dict()["code"] == "KOR-PDF-001"


@pytest.mark.unit
def test_subclasses_inherit_base():
    assert issubclass(ConfigError, KorrektorError)
    assert issubclass(PdfError, KorrektorError)
