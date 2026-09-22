"""Ein Satz -> Prompt -> LLM -> Kandidaten -> Spans, mit Retry-Schleife.

Bei Formatbruch (``ParseError``) wird einmal erneut gefragt, mit dem Hinweis auf
das erwartete Format (Agentic-Retry-Muster aus Woche 10). Scheitert auch das,
gilt der Satz als "keine Entitaeten" und wird als ``parse_ok=False`` markiert –
die Schema-Fehlerquote ist selbst eine Messgroesse (Ablation E7).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from promptner.config import get_logger
from promptner.domain import Prediction, PromptConfig, Sentence
from promptner.errors import ParseError
from promptner.llm.cache import ResponseCache, cache_key
from promptner.llm.client import ChatRequest, LlmClient
from promptner.llm.parser import align, parse_answer
from promptner.prompting.builder import build_prompt

log = get_logger("pipeline.predict")

_RETRY_HINT = {
    "text": (
        "Your previous answer did not follow the required format. Answer ONLY with numbered "
        "lines of the form `N. <text> | True or False | <explanation> (<type>)`, or `None` "
        "if there are no candidates."
    ),
    "json": (
        "Your previous answer was not valid JSON. Answer ONLY with one JSON object of the form "
        '{"candidates": [{"text": "...", "is_entity": true, "explanation": "...", "type_name": "..."}]}.'
    ),
}


def _ask(
    client: LlmClient, request: ChatRequest, cache: ResponseCache | None, model: str | None
) -> str:
    key = cache_key(model or "default", request, None) if cache is not None else None
    if cache is not None and key is not None:
        hit = cache.get(key)
        if hit is not None:
            return hit
    raw = client.complete(request)
    if cache is not None and key is not None:
        cache.put(key, raw)
    return raw


def predict_sentence(
    sentence: Sentence,
    config: PromptConfig,
    client: LlmClient,
    *,
    cache: ResponseCache | None = None,
    model: str | None = None,
) -> Prediction:
    request = build_prompt(config, sentence)
    if model is not None:
        request = replace(request, model=model)
    raw = ""
    retries = 0
    while True:
        raw = _ask(client, request, cache, model)
        try:
            candidates = parse_answer(raw, config)
            break
        except ParseError as exc:
            if retries >= config.max_retries:
                log.warning(
                    "Satz %s: Antwort unparsebar nach %d Versuch(en): %s",
                    sentence.id,
                    retries + 1,
                    exc.message,
                )
                return Prediction(sentence_id=sentence.id, raw=raw, parse_ok=False, retries=retries)
            retries += 1
            hint = _RETRY_HINT[config.output_format]
            request = replace(request, user=f"{request.user}\n\n{hint}")
    spans, unmatched, unknown = align(sentence, candidates, config.dataset)
    return Prediction(
        sentence_id=sentence.id,
        spans=spans,
        candidates=candidates,
        raw=raw,
        parse_ok=True,
        retries=retries,
        n_unmatched=unmatched,
        n_unknown_type=unknown,
    )


def predict_many(
    sentences: list[Sentence],
    config: PromptConfig,
    client: LlmClient,
    *,
    workers: int = 1,
    cache: ResponseCache | None = None,
    model: str | None = None,
    on_progress=None,
) -> list[Prediction]:
    """Vorhersagen fuer viele Saetze, Reihenfolge bleibt erhalten."""

    def _one(s: Sentence) -> Prediction:
        p = predict_sentence(s, config, client, cache=cache, model=model)
        if on_progress is not None:
            on_progress()
        return p

    if workers <= 1:
        return [_one(s) for s in sentences]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_one, sentences))
