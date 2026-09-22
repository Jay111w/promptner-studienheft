"""Absatz (1-10 Saetze) -> Prompt -> LLM -> Kandidaten -> Spans je Satz, mit Retry-Schleife.

Mehrere Saetze werden zu einem "Paragraph" (Figure 1) verkettet und in einem Aufruf
gefragt; die gefundenen Spans werden ueber Token-Offsets auf die Saetze zurueckverteilt.

Bei Formatbruch (``ParseError``) wird einmal erneut gefragt, mit dem Hinweis auf
das erwartete Format (Agentic-Retry-Muster aus Woche 10). Scheitert auch das,
gilt der Satz als "keine Entitaeten" und wird als ``parse_ok=False`` markiert –
die Schema-Fehlerquote ist selbst eine Messgroesse (Ablation E7).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from promptner.config import get_logger
from promptner.domain import Prediction, PromptConfig, Sentence, Span
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


def _merge(sentences: list[Sentence]) -> tuple[Sentence, list[int]]:
    """Verkettet Saetze zu einem Absatz; liefert auch die Token-Offsets je Satz."""
    tokens: list[str] = []
    offsets: list[int] = []
    for s in sentences:
        offsets.append(len(tokens))
        tokens.extend(s.tokens)
    return Sentence(id="+".join(s.id for s in sentences), tokens=tokens), offsets


def _split_spans(spans: list[Span], offsets: list[int], lengths: list[int]) -> list[list[Span]]:
    """Absatz-Spans auf Saetze verteilen; Spans ueber Satzgrenzen werden verworfen."""
    out: list[list[Span]] = [[] for _ in offsets]
    for sp in spans:
        for i, (off, n) in enumerate(zip(offsets, lengths, strict=True)):
            if off <= sp.start and sp.end <= off + n:
                out[i].append(Span(start=sp.start - off, end=sp.end - off, label=sp.label))
                break
    return out


def predict_paragraph(
    sentences: list[Sentence],
    config: PromptConfig,
    client: LlmClient,
    *,
    cache: ResponseCache | None = None,
    model: str | None = None,
) -> list[Prediction]:
    """Ein LLM-Aufruf fuer 1..n Saetze; eine Prediction je Satz, Diagnosewerte beim ersten."""
    paragraph, offsets = _merge(sentences)
    request = build_prompt(config, paragraph)
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
                    "Absatz %s: Antwort unparsebar nach %d Versuch(en): %s",
                    paragraph.id,
                    retries + 1,
                    exc.message,
                )
                return [
                    Prediction(
                        sentence_id=s.id, raw=raw, parse_ok=False, retries=retries if i == 0 else 0
                    )
                    for i, s in enumerate(sentences)
                ]
            retries += 1
            hint = _RETRY_HINT[config.output_format]
            request = replace(request, user=f"{request.user}\n\n{hint}")
    spans, unmatched, unknown = align(paragraph, candidates, config.dataset)
    per_sentence = _split_spans(spans, offsets, [len(s.tokens) for s in sentences])
    return [
        Prediction(
            sentence_id=s.id,
            spans=sp,
            candidates=candidates,
            raw=raw,
            parse_ok=True,
            retries=retries if i == 0 else 0,  # Absatz-Diagnosen nur einmal zaehlen
            n_unmatched=unmatched if i == 0 else 0,
            n_unknown_type=unknown if i == 0 else 0,
        )
        for i, (s, sp) in enumerate(zip(sentences, per_sentence, strict=True))
    ]


def predict_sentence(
    sentence: Sentence,
    config: PromptConfig,
    client: LlmClient,
    *,
    cache: ResponseCache | None = None,
    model: str | None = None,
) -> Prediction:
    return predict_paragraph([sentence], config, client, cache=cache, model=model)[0]


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
    """Vorhersagen fuer viele Saetze, je ``paragraph_size`` Saetze pro Aufruf; Reihenfolge bleibt."""
    n = config.paragraph_size
    chunks = [sentences[i : i + n] for i in range(0, len(sentences), n)]

    def _one(chunk: list[Sentence]) -> list[Prediction]:
        preds = predict_paragraph(chunk, config, client, cache=cache, model=model)
        if on_progress is not None:
            for _ in chunk:
                on_progress()
        return preds

    if workers <= 1:
        results = [_one(c) for c in chunks]
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_one, chunks))
    return [p for preds in results for p in preds]
