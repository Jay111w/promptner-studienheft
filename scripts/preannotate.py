"""Vorschlaege fuer die Studienheft-Annotation erzeugen (Silber-Labels).

Das Modell beschriftet die Saetze aus ``raw.jsonl`` vor, damit die beiden
Annotatoren korrigieren statt bei Null anzufangen. Die Vorschlaege sind
ausdruecklich *kein* Gold: jeder Satz wird von Hand geprueft.

Der gemeinsame Block fuer die Uebereinstimmungsmessung bleibt unbeschriftet
(siehe ``scripts/split_annotation.py``), sonst misst Cohen's Kappa nur noch,
wie aehnlich zwei Menschen denselben Maschinenvorschlag durchwinken.

    uv run scripts/preannotate.py \
        --inp data/studienheft/raw.jsonl \
        --out data/studienheft/vorschlag.jsonl
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from tqdm import tqdm

from promptner.config import get_settings, setup_logging
from promptner.data import load_jsonl, save_jsonl
from promptner.domain import PromptConfig, Sentence
from promptner.llm.cache import ResponseCache
from promptner.llm.client import LlmClient
from promptner.pipeline.predict import predict_many

app = typer.Typer(add_completion=False)


@app.command()
def main(
    inp: Annotated[Path, typer.Option(help="Vorlage aus annotate_template.py")] = Path(
        "data/studienheft/raw.jsonl"
    ),
    out: Annotated[Path, typer.Option(help="Zieldatei mit Vorschlaegen")] = Path(
        "data/studienheft/vorschlag.jsonl"
    ),
    model: Annotated[str | None, typer.Option(help="Modell-ID; Standard: LLM_MODEL")] = None,
    limit: Annotated[int | None, typer.Option(help="Nur die ersten n Saetze")] = None,
) -> None:
    s = get_settings()
    setup_logging(level=s.log_level, log_dir=s.log_dir)

    sentences = load_jsonl(inp)
    if limit is not None:
        sentences = sentences[:limit]

    config = PromptConfig(dataset="studienheft", k_examples=5, seed=1)
    client = LlmClient(settings=s)
    cache = ResponseCache(Path(s.cache_dir))
    try:
        with tqdm(total=len(sentences), unit="Satz") as bar:
            preds = predict_many(
                sentences,
                config,
                client,
                workers=s.llm_max_workers,
                cache=cache,
                model=model,
                on_progress=bar.update,
            )
    finally:
        cache.close()

    by_id = {p.sentence_id: p for p in preds}
    labelled = [
        Sentence(
            id=sent.id,
            tokens=sent.tokens,
            spans=by_id[sent.id].spans if sent.id in by_id else [],
            source=sent.source,
        )
        for sent in sentences
    ]
    save_jsonl(labelled, out)

    n_spans = sum(len(x.spans) for x in labelled)
    n_with = sum(1 for x in labelled if x.spans)
    n_failed = sum(1 for p in preds if not p.parse_ok)
    typer.echo(f"-> {out}")
    typer.echo(f"   {len(labelled)} Saetze, {n_spans} Vorschlaege, {n_with} Saetze mit Entitaet")
    if n_failed:
        typer.echo(f"   {n_failed} Saetze ohne verwertbare Antwort (bitte von Hand pruefen)")


if __name__ == "__main__":
    app()
