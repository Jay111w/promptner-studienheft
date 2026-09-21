"""Unit-Tests fuer die Vorhersage-Pipeline (Retry, Batch, Cache) mit Fake-Client."""

import pytest

from promptner.domain import PromptConfig, Sentence, Span
from promptner.llm.client import ChatRequest, LlmClient
from promptner.pipeline.predict import predict_many, predict_sentence

CFG = PromptConfig(dataset="conll2003", k_examples=2)
SENT = Sentence(id="s1", tokens=["Ohio", "is", "a", "state", "."])
GOOD = "1. Ohio | True | as it is a state (location)\n2. state | False | common noun"


class _ScriptedClient(LlmClient):
    """Liefert vorgegebene Antworten der Reihe nach; zaehlt Anfragen und merkt Prompts."""

    def __init__(self, answers):
        self._answers = list(answers)
        self.requests: list[ChatRequest] = []
        self.calls_made = 0

    def complete(self, request):
        self.requests.append(request)
        self.calls_made += 1
        return self._answers.pop(0)


@pytest.mark.unit
def test_predict_happy_path():
    client = _ScriptedClient([GOOD])
    p = predict_sentence(SENT, CFG, client)
    assert p.spans == [Span(start=0, end=1, label="LOC")]
    assert p.parse_ok and p.retries == 0 and p.raw == GOOD
    assert len(p.candidates) == 2


@pytest.mark.unit
def test_retry_once_after_garbage_then_success():
    client = _ScriptedClient(["I cannot do that.", GOOD])
    p = predict_sentence(SENT, CFG, client)
    assert p.parse_ok and p.retries == 1 and p.spans[0].label == "LOC"
    # Der zweite Prompt enthaelt einen Format-Hinweis
    assert "format" in client.requests[1].user.lower()
    assert len(client.requests) == 2


@pytest.mark.unit
def test_gives_up_after_max_retries():
    client = _ScriptedClient(["garbage", "still garbage"])
    p = predict_sentence(SENT, CFG, client)
    assert p.parse_ok is False and p.spans == [] and p.retries == 1
    assert p.raw == "still garbage"


@pytest.mark.unit
def test_no_retry_when_disabled():
    client = _ScriptedClient(["garbage"])
    p = predict_sentence(SENT, PromptConfig(dataset="conll2003", max_retries=0), client)
    assert p.parse_ok is False and len(client.requests) == 1


@pytest.mark.unit
def test_diagnostics_propagate():
    client = _ScriptedClient(
        ["1. Nevada | True | a state (location)\n2. Ohio | True | a state (galaxy)"]
    )
    p = predict_sentence(SENT, CFG, client)
    assert p.n_unmatched == 1 and p.n_unknown_type == 1 and p.spans == []


@pytest.mark.unit
def test_predict_many_keeps_order_with_workers(tmp_path):
    sents = [Sentence(id=f"s{i}", tokens=["Ohio", "is", str(i)]) for i in range(6)]
    client = _ScriptedClient([GOOD] * 6)
    preds = predict_many(sents, CFG, client, workers=3)
    assert [p.sentence_id for p in preds] == [s.id for s in sents]
    assert all(p.spans == [Span(start=0, end=1, label="LOC")] for p in preds)


@pytest.mark.unit
def test_cache_avoids_second_call(tmp_path):
    from promptner.llm.cache import ResponseCache

    cache = ResponseCache(tmp_path / "c")
    client = _ScriptedClient([GOOD])
    p1 = predict_sentence(SENT, CFG, client, cache=cache, model="m")
    p2 = predict_sentence(SENT, CFG, client, cache=cache, model="m")
    assert p1.spans == p2.spans and client.calls_made == 1
    # anderes Modell -> neuer Aufruf
    client2 = _ScriptedClient([GOOD])
    predict_sentence(SENT, CFG, client2, cache=cache, model="other")
    assert client2.calls_made == 1
