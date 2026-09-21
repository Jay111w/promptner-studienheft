"""Schickt 3 Saetze an den echten KISSKI-Endpunkt (braucht KISSKI_API_KEY; in CI uebersprungen)."""

import os

import pytest

from promptner.config.settings import Settings
from promptner.data import load_conll2003
from promptner.domain import PromptConfig
from promptner.llm.client import LlmClient
from promptner.pipeline import predict_many

pytestmark = [pytest.mark.live, pytest.mark.network]


@pytest.mark.skipif(not os.environ.get("KISSKI_API_KEY"), reason="KISSKI_API_KEY nicht gesetzt")
def test_three_sentences_end_to_end():
    settings = Settings()
    sents = load_conll2003("validation", limit=3)
    preds = predict_many(
        sents, PromptConfig(dataset="conll2003", k_examples=2), LlmClient(settings=settings)
    )
    assert len(preds) == 3
    assert any(p.parse_ok for p in preds)
