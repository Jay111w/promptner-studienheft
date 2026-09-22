"""Erster echter Lauf: PromptNER auf einer CoNLL-Dev-Teilmenge (braucht KISSKI_API_KEY).

uv run scripts/run_smoke.py --limit 200
uv run scripts/run_smoke.py --dataset germeval14 --limit 100 --model llama-3.3-70b-instruct
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Annotated

import typer
from tqdm import tqdm

from promptner.config import get_settings, setup_logging
from promptner.data import load_by_name
from promptner.domain import PromptConfig
from promptner.eval import evaluate
from promptner.llm.cache import ResponseCache
from promptner.llm.client import LlmClient
from promptner.pipeline import predict_many
from promptner.prompting import prompt_hash

app = typer.Typer(add_completion=False)


@app.command()
def main(
    dataset: Annotated[str, typer.Option(help="conll2003 | germeval14")] = "conll2003",
    split: Annotated[str, typer.Option()] = "validation",
    limit: Annotated[int, typer.Option(help="Anzahl Saetze")] = 200,
    model: Annotated[
        str | None, typer.Option(help="Modell-ID am Endpunkt; Standard aus .env")
    ] = None,
    k: Annotated[int, typer.Option(help="Few-Shot-Beispiele: 0, 2, 5, 10")] = 5,
    paragraph: Annotated[int, typer.Option(help="Saetze je Aufruf (1-10)")] = 2,
    workers: Annotated[int | None, typer.Option()] = None,
) -> None:
    s = get_settings()
    setup_logging(level=s.log_level, log_dir=s.log_dir)
    model_id = model or s.llm_model
    config = PromptConfig(dataset=dataset, k_examples=k, paragraph_size=paragraph)  # type: ignore[arg-type]
    sentences = load_by_name(dataset, split, limit=limit)  # type: ignore[arg-type]
    client = LlmClient(settings=s)
    cache = ResponseCache(Path(s.cache_dir))

    typer.echo(
        f"{len(sentences)} Saetze | {model_id} | {config.short_name()} | prompt {prompt_hash(config)}"
    )
    t0 = time.time()
    with tqdm(total=len(sentences), unit="Satz") as bar:
        preds = predict_many(
            sentences,
            config,
            client,
            workers=workers or s.llm_max_workers,
            cache=cache,
            model=model_id,
            on_progress=bar.update,
        )
    elapsed = time.time() - t0
    result = evaluate(sentences, [p.spans for p in preds])

    out_dir = Path(s.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"smoke_{dataset}_{model_id}_{config.short_name()}.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["sentence_id", "gold", "pred", "parse_ok", "retries", "n_unmatched", "n_unknown_type"]
        )
        for sent, p in zip(sentences, preds, strict=True):
            w.writerow(
                [
                    sent.id,
                    ";".join(f"{sp.text(sent.tokens)}/{sp.label}" for sp in sent.spans),
                    ";".join(f"{sp.text(sent.tokens)}/{sp.label}" for sp in p.spans),
                    int(p.parse_ok),
                    p.retries,
                    p.n_unmatched,
                    p.n_unknown_type,
                ]
            )

    parse_fail = sum(not p.parse_ok for p in preds)
    typer.echo(
        f"\nF1={result.f1:.4f} P={result.precision:.4f} R={result.recall:.4f} | "
        f"parse_fail={parse_fail} retries={sum(p.retries for p in preds)} "
        f"unmatched={sum(p.n_unmatched for p in preds)} unknown_type={sum(p.n_unknown_type for p in preds)} | "
        f"{elapsed:.0f}s, {client.calls_made} API-Aufrufe"
    )
    for label, ts in sorted(result.per_type.items()):
        typer.echo(
            f"  {label:5s} F1={ts.f1:.3f} P={ts.precision:.3f} R={ts.recall:.3f} n={ts.support}"
        )
    typer.echo(f"-> {out}")
    cache.close()


if __name__ == "__main__":
    app()
