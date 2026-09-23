"""Antwort-Cache als konsistente Kopie exportieren, damit Fremde die Laeufe nachspielen koennen.

Der Arbeits-Cache (`.cache/llm`) ist gitignoriert und wird waehrend laufender Experimente
geschrieben; ein blosses `cp` der SQLite-Datei waehrend eines Laufs liefert eine unvollstaendige
Kopie (die neuen Eintraege stehen noch im Write-Ahead-Log). Dieses Skript nutzt deshalb die
Backup-API von SQLite, die eine in sich stimmige Kopie erzeugt - auch bei offener Datenbank.

    uv run scripts/export_cache.py                  # .cache/llm -> replay-cache/
    CACHE_DIR=replay-cache uv run promptner run --experiment E4   # nachspielen, ohne API-Key

Die Kopie ist klein genug fuers Repository (rund 1-2 MB) und enthaelt nur Prompts und Antworten
der oeffentlichen Datensaetze, keine Schluessel.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Annotated

import typer

from promptner.config import get_settings

app = typer.Typer(add_completion=False)


def backup_sqlite(source: Path, target: Path) -> int:
    """Konsistente Kopie einer (auch offenen) SQLite-Datei; liefert die Groesse in Bytes."""
    if not source.is_file():
        raise typer.BadParameter(f"Keine Cache-Datenbank unter {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return target.stat().st_size


@app.command()
def main(
    source: Annotated[
        str | None, typer.Option(help="Cache-Verzeichnis; Standard CACHE_DIR aus .env")
    ] = None,
    out: Annotated[str, typer.Option(help="Zielverzeichnis fuer die Kopie")] = "replay-cache",
) -> None:
    src_dir = Path(source or get_settings().cache_dir)
    target = Path(out) / "cache.db"
    size = backup_sqlite(src_dir / "cache.db", target)

    from promptner.llm.cache import ResponseCache

    cache = ResponseCache(Path(out))
    n = len(cache)
    cache.close()
    typer.echo(f"{n} Antworten, {size / 1_000_000:.1f} MB -> {target}")
    typer.echo(f"Nachspielen: CACHE_DIR={out} uv run promptner run --experiment E4")


if __name__ == "__main__":
    app()
