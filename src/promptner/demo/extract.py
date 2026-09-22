"""PDF-Seiten -> Saetze -> PromptNER -> Entitaeten-Tabelle (Demo-Modus der Oberflaeche).

Kein Qt hier: die Funktionen sind mit Fake-Client testbar und werden vom UI-Worker aufgerufen.
Standard-Konfiguration ist die deutsche (GermEval-Typen PER/ORG/LOC/OTH), weil Studienhefte
deutsch sind.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from promptner.data.segment import segment_text
from promptner.domain import PromptConfig
from promptner.llm.cache import ResponseCache
from promptner.llm.client import LlmClient
from promptner.pipeline import predict_many

DEFAULT_CONFIG = PromptConfig(dataset="germeval14", k_examples=5)


class EntityHit(BaseModel):
    """Eine gefundene Entitaet mit Fundstelle."""

    pdf_page: int  # 0-basiert
    text: str
    label: str
    sentence: str


def extract_entities(
    pages: list[tuple[int, str]],
    client: LlmClient,
    *,
    config: PromptConfig = DEFAULT_CONFIG,
    model: str | None = None,
    cache: ResponseCache | None = None,
    workers: int = 2,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[EntityHit]:
    """``pages``: (pdf_page, text). Liefert Treffer in Lesereihenfolge."""
    sentences = []
    page_of: dict[str, int] = {}
    for pdf_page, text in pages:
        for s in segment_text(text, source=f"seite-{pdf_page + 1}"):
            sentences.append(s)
            page_of[s.id] = pdf_page
    if not sentences:
        return []
    total = len(sentences)
    done = 0

    def _tick() -> None:
        nonlocal done
        done += 1
        if on_progress is not None:
            on_progress(done, total)

    preds = predict_many(
        sentences, config, client, workers=workers, cache=cache, model=model, on_progress=_tick
    )
    hits: list[EntityHit] = []
    for s, p in zip(sentences, preds, strict=True):
        for sp in p.spans:
            hits.append(
                EntityHit(
                    pdf_page=page_of[s.id],
                    text=" ".join(s.tokens[sp.start : sp.end]),
                    label=sp.label,
                    sentence=s.text,
                )
            )
    return hits


def extract_from_pdf(
    path: str | Path,
    client: LlmClient,
    *,
    first_page: int = 0,
    last_page: int | None = None,
    **kwargs,
) -> list[EntityHit]:
    """Oeffnet das PDF mit dem Korrektor-Extraktor und extrahiert Entitaeten seitenweise."""
    from korrektor.domain import PageRange
    from korrektor.services.pdf.extractor import PdfDocument

    with PdfDocument(path) as doc:
        end = doc.page_count - 1 if last_page is None else min(last_page, doc.page_count - 1)
        page_texts = doc.extract_range(PageRange(start=first_page, end=end))
    return extract_entities([(p.pdf_page, p.text) for p in page_texts], client, **kwargs)
