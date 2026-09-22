"""Kommandozeile: ``promptner run | summary | plots | models``."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from tqdm import tqdm

from promptner.config import get_settings, setup_logging
from promptner.experiments.aggregate import collect, summarize, write_summary
from promptner.experiments.runner import STUDIENHEFT_GOLD, run_all
from promptner.experiments.spec import build_experiment

app = typer.Typer(add_completion=False, help="PromptNER-Experimente ausfuehren und auswerten.")


def _split_list(value: str | None) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()] if value else []


@app.command()
def run(
    experiment: Annotated[str, typer.Option(help="E1-E8")],
    models: Annotated[
        str | None, typer.Option(help="Kommagetrennte Modell-IDs; Standard: LLM_MODEL aus .env")
    ] = None,
    seeds: Annotated[str, typer.Option(help="Kommagetrennt, z. B. 1,2,3")] = "1,2,3",
    limit: Annotated[int | None, typer.Option(help="Saetze je Lauf (None = alle)")] = 300,
    datasets: Annotated[str | None, typer.Option(help="Nur E1/E2: kommagetrennt")] = None,
    workers: Annotated[int | None, typer.Option()] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Nur Laeufe auflisten")] = False,
) -> None:
    s = get_settings()
    setup_logging(level=s.log_level, log_dir=s.log_dir)
    model_list = _split_list(models) or [s.llm_model]
    seed_list = [int(x) for x in _split_list(seeds)]
    specs = build_experiment(
        experiment,
        models=model_list,
        seeds=seed_list,
        limit=limit,
        datasets=_split_list(datasets) or None,
        studienheft_gold=STUDIENHEFT_GOLD,
    )
    typer.echo(f"{experiment}: {len(specs)} Laeufe")
    for sp in specs:
        typer.echo(f"  {sp.run_id}")
    if dry_run:
        return

    from promptner.llm.cache import ResponseCache
    from promptner.llm.client import LlmClient

    client = LlmClient(settings=s)
    cache = ResponseCache(Path(s.cache_dir))
    with tqdm(total=len(specs), unit="Lauf") as bar:
        records = run_all(
            specs,
            client=client,
            cache=cache,
            results_dir=s.results_dir,
            workers=workers or s.llm_max_workers,
            on_run_done=lambda _r: bar.update(),
        )
    cache.close()
    for r in records:
        flag = " (resumed)" if r.resumed else ""
        typer.echo(f"  F1={r.f1:.4f}  parse_fail={r.parse_fail}  {r.run_id}{flag}")
    out = write_summary(s.results_dir)
    typer.echo(f"-> {out}")


@app.command()
def summary() -> None:
    """Aggregiert alle Laeufe zu results/summary.csv und zeigt die Tabelle."""
    s = get_settings()
    df = summarize(collect(s.results_dir))
    if df.empty:
        typer.echo("Keine Laeufe gefunden.")
        raise typer.Exit(code=0)
    cols = [
        "experiment",
        "dataset",
        "model",
        "variant",
        "n",
        "f1_mean",
        "f1_std",
        "parse_fail_mean",
        "unmatched_mean",
    ]
    typer.echo(df[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    typer.echo(f"-> {write_summary(s.results_dir)}")


@app.command()
def plots() -> None:
    """Erzeugt je Experiment ein PNG unter results/plots/."""
    from promptner.eval.plots import plot_experiment

    s = get_settings()
    df = summarize(collect(s.results_dir))
    for exp in sorted(df["experiment"].unique()) if not df.empty else []:
        out = plot_experiment(df, exp, Path(s.results_dir) / "plots" / f"{exp}.png")
        typer.echo(f"-> {out}")


@app.command()
def models() -> None:
    """Listet die am Endpunkt verfuegbaren Modelle (braucht KISSKI_API_KEY)."""
    from openai import OpenAI

    from promptner.llm import list_model_ids

    s = get_settings()
    sdk = OpenAI(base_url=s.llm_base_url, api_key=s.require_api_key())
    for mid in list_model_ids(sdk):
        typer.echo(mid)


if __name__ == "__main__":
    app()
