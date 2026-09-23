"""Erzeugt eine JSONL-Vorlage fuer das Studienheft-Sample (Spans leer, zum Ausfuellen).

    uv run scripts/annotate_template.py heft.pdf --pages 5-8 --out data/studienheft/raw.jsonl
    uv run scripts/annotate_template.py notizen.txt --out data/studienheft/raw.jsonl

Anleitung zum Annotieren: data/studienheft/ANNOTATION.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from promptner.data import save_jsonl
from promptner.data.segment import segment_text

app = typer.Typer(add_completion=False)


def _read(path: Path, pages: str | None) -> str:
    if path.suffix.lower() != ".pdf":
        return path.read_text(encoding="utf-8")
    from korrektor.domain import PageRange
    from korrektor.services.pdf.extractor import PdfDocument
    from promptner.data.segment import strip_repeated_lines

    with PdfDocument(path) as doc:
        if pages:
            a, _, b = pages.partition("-")
            rng = PageRange(start=int(a) - 1, end=int(b or a) - 1)
        else:
            rng = PageRange(start=0, end=doc.page_count - 1)
        # Seitenweise, damit die auf jeder Seite wiederkehrende Kopfzeile erkennbar bleibt.
        return strip_repeated_lines(p.text for p in doc.extract_range(rng))


@app.command()
def main(
    source: Annotated[Path, typer.Argument(exists=True, help="PDF oder Textdatei")],
    out: Annotated[Path, typer.Option(help="Ziel-JSONL")] = Path("data/studienheft/raw.jsonl"),
    pages: Annotated[str | None, typer.Option(help="Seitenbereich 1-basiert, z. B. 5-8")] = None,
    min_tokens: Annotated[int, typer.Option(help="Kuerzere Fragmente verwerfen")] = 4,
) -> None:
    text = _read(source, pages)
    sentences = segment_text(text, source="studienheft", min_tokens=min_tokens)
    save_jsonl(sentences, out)
    typer.echo(f"{len(sentences)} Saetze -> {out}")


if __name__ == "__main__":
    app()
