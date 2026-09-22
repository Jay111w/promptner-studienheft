"""BERT-Baseline (E9) trainieren und wie einen PromptNER-Lauf ablegen.

uv run --extra bert scripts/train_bert.py                       # CoNLL-2003, 3 Epochen, Dev-150
uv run --extra bert scripts/train_bert.py --eval test:0         # Test-Set komplett
uv run --extra bert scripts/train_bert.py --train-limit 200 --epochs 1       # Rauchtest

Deutsche Baseline (GermEval 2014), Gegenstueck zu den GermEval-Prompt-Laeufen:

uv run --extra bert scripts/train_bert.py --dataset germeval14 --model deepset/gbert-base
"""

from __future__ import annotations

from typing import Annotated

import typer

from promptner.baseline.bert import TrainConfig, train_and_evaluate
from promptner.config import setup_logging
from promptner.config.settings import get_settings

app = typer.Typer(add_completion=False)


@app.command()
def main(
    dataset: Annotated[str, typer.Option(help="conll2003 oder germeval14")] = "conll2003",
    epochs: Annotated[int, typer.Option()] = 3,
    seed: Annotated[int, typer.Option()] = 1,
    train_limit: Annotated[int, typer.Option(help="0 = alle 14k Saetze")] = 0,
    eval: Annotated[
        str, typer.Option(help="Split:Limit, kommagetrennt; 0 = alle")
    ] = "validation:150,test:0",
    model: Annotated[str, typer.Option()] = "bert-base-cased",
) -> None:
    s = get_settings()
    setup_logging(level=s.log_level, log_dir=s.log_dir)
    cfg = TrainConfig(
        dataset=dataset,
        model_name=model,
        epochs=epochs,
        seed=seed,
        train_limit=train_limit or None,
        eval_splits=tuple(
            (part.split(":")[0], int(part.split(":")[1]) or None) for part in eval.split(",")
        ),
    )
    for summary in train_and_evaluate(cfg, results_dir=s.results_dir):
        typer.echo(
            f"{summary['split']}: F1={summary['f1']:.4f} P={summary['precision']:.4f} "
            f"R={summary['recall']:.4f} | {summary['n_sentences']} Saetze | "
            f"Training {summary['elapsed_s']}s auf {summary['device']}"
        )
        typer.echo(f"-> {s.results_dir}/runs/{summary['run_id']}")


if __name__ == "__main__":
    app()
