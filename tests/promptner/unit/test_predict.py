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


# --- Absatz-Buendelung: mehrere Saetze je Aufruf (Paper: "Paragraph"), Budget-Schonung ---

PARA = [
    Sentence(id="p1", tokens=["Ohio", "is", "big", "."]),
    Sentence(id="p2", tokens=["Paris", "too", "."]),
    Sentence(id="p3", tokens=["Nothing", "here", "."]),
]
PARA_ANSWER = (
    "1. Ohio | True | a state (location)\n"
    "2. Paris | True | a city (location)\n"
    "3. Nothing | False | pronoun\n"
    "4. Mars | True | not in text (location)"
)


@pytest.mark.unit
def test_paragraph_batches_sentences_into_one_call_and_splits_spans():
    cfg = PromptConfig(dataset="conll2003", k_examples=2, paragraph_size=3)
    client = _ScriptedClient([PARA_ANSWER])
    preds = predict_many(PARA, cfg, client, workers=1)
    assert client.calls_made == 1
    assert "Paragraph: Ohio is big . Paris too . Nothing here ." in client.requests[0].user
    assert [p.sentence_id for p in preds] == ["p1", "p2", "p3"]
    assert preds[0].spans == [Span(start=0, end=1, label="LOC")]
    assert preds[1].spans == [Span(start=0, end=1, label="LOC")]  # Offset zurueckgerechnet
    assert preds[2].spans == []
    # Diagnosewerte nur einmal je Absatz (beim ersten Satz), sonst doppelt gezaehlt
    assert preds[0].n_unmatched == 1 and preds[1].n_unmatched == 0
    assert all(p.parse_ok for p in preds) and all(p.raw == PARA_ANSWER for p in preds)


@pytest.mark.unit
def test_paragraph_parse_failure_marks_every_sentence():
    cfg = PromptConfig(dataset="conll2003", k_examples=2, paragraph_size=3, max_retries=0)
    preds = predict_many(
        PARA, PromptConfig(**cfg.model_dump()), _ScriptedClient(["garbage"]), workers=1
    )
    assert [p.parse_ok for p in preds] == [False, False, False]
    assert all(p.spans == [] for p in preds)


@pytest.mark.unit
def test_paragraph_size_one_equals_sentence_mode():
    cfg = PromptConfig(dataset="conll2003", k_examples=2, paragraph_size=1)
    client = _ScriptedClient([GOOD, "None", "None"])
    preds = predict_many([SENT, PARA[1], PARA[2]], cfg, client, workers=1)
    assert client.calls_made == 3 and preds[0].spans[0].label == "LOC"


@pytest.mark.unit
def test_paragraph_size_in_short_name():
    assert PromptConfig(dataset="conll2003").short_name().endswith("_s1_p2")
    assert PromptConfig(dataset="conll2003", paragraph_size=1).short_name().endswith("_s1_p1")
