"""Kommandozeile: ``promptner run | summary | plots | errors | agreement | models``."""

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
    seeds: Annotated[str, typer.Option(help="Kommagetrennt, z. B. 1,2,3")] = "1,2",
    limit: Annotated[int | None, typer.Option(help="Saetze je Lauf (None = alle)")] = 150,
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
def errors(
    run: Annotated[str, typer.Option(help="run_id unter results/runs/ oder Pfad zum Lauf-Ordner")],
    examples: Annotated[int, typer.Option(help="Beispielsaetze im Bericht")] = 10,
    out: Annotated[
        str | None, typer.Option(help="Zieldatei; Standard results/errors/<run_id>.md")
    ] = None,
    png: Annotated[bool, typer.Option(help="Verwechslungsmatrix auch als Heatmap-PNG")] = True,
) -> None:
    """Fehleranalyse eines Laufs: Verwechslungsmatrix, Grenzfehler, Halluzinationen, Beispiele."""
    from promptner.eval.error_analysis import analyze_run, render_markdown

    s = get_settings()
    run_dir = Path(run) if Path(run).is_dir() else Path(s.results_dir) / "runs" / run
    if not (run_dir / "predictions.jsonl").is_file():
        typer.echo(f"Kein Lauf unter {run_dir}")
        raise typer.Exit(code=1)
    rep = analyze_run(run_dir)
    target = Path(out) if out else Path(s.results_dir) / "errors" / f"{rep.run_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(rep, max_examples=examples), encoding="utf-8")
    if png:
        from promptner.eval.error_analysis import NONE
        from promptner.eval.plots import plot_confusion

        labels = sorted(({g for g, _ in rep.matrix} | {p for _, p in rep.matrix}) - {NONE})
        png_path = plot_confusion(
            rep.matrix, labels, target.with_suffix(".png"), title=rep.run_id.split("__")[-1]
        )
        typer.echo(f"-> {png_path}")
    for kind in ("correct", "type", "boundary", "boundary+type", "missed", "spurious"):
        typer.echo(f"  {kind:14s} {rep.counts.get(kind, 0)}")
    typer.echo(
        f"  halluziniert {rep.n_unmatched} | unbekannter Typ {rep.n_unknown_type} | "
        f"Format-Fehler {rep.n_parse_fail} | Retries {rep.n_retries}"
    )
    typer.echo(f"-> {target}")


@app.command()
def agreement(
    a: Annotated[str, typer.Option("--a", help="JSONL der ersten Annotatorin")],
    b: Annotated[str, typer.Option("--b", help="JSONL der zweiten Annotatorin")],
    out: Annotated[
        str | None, typer.Option(help="Zieldatei; Standard docs/annotator-agreement.md")
    ] = None,
    examples: Annotated[int, typer.Option(help="Uneinige Saetze im Bericht")] = 20,
) -> None:
    """Uebereinstimmung zweier Annotationen: Span-F1, Cohen's Kappa, uneinige Saetze."""
    from promptner.data import load_jsonl
    from promptner.eval.agreement import compare, render_markdown

    setup_logging(level=get_settings().log_level)
    rep = compare(load_jsonl(a), load_jsonl(b))
    target = Path(out) if out else Path("docs/annotator-agreement.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(rep, max_examples=examples), encoding="utf-8")
    typer.echo(f"  Saetze gemeinsam   {rep.n_sentences}")
    typer.echo(f"  Span-F1            {rep.span_f1:.3f}")
    typer.echo(f"  Kappa je Token     {rep.token_kappa:.3f}")
    typer.echo(f"  uneinige Saetze    {len(rep.disagreements)}")
    if rep.unknown_labels:
        typer.echo(f"  ACHTUNG unbekannte Labels: {', '.join(sorted(rep.unknown_labels))}")
    typer.echo(f"-> {target}")


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
