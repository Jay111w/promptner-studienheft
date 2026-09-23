"""Die Studienheft-Vorlage auf zwei Annotatoren aufteilen.

Drei Sorten Datei entstehen:

``gold_gemeinsam_VORLAGE.jsonl``
    Der ueberlappende Block. **Ohne** Vorschlaege, denn nur dieser Block geht in
    die Uebereinstimmungsmessung ein. Beide bearbeiten ihn unabhaengig; wer hier
    einen Maschinenvorschlag durchwinkt, misst die Uebereinstimmung kaputt.

``vorschlag_<name>.jsonl``
    Der persoenliche Block, mit Vorschlaegen des Modells. Hier wird korrigiert,
    nicht neu geschrieben.

Die Aufteilung ist deterministisch (fester Seed), damit sie nachvollziehbar
bleibt. Der gemeinsame Block wird gleichmaessig ueber das Dokument gestreut,
damit er nicht zufaellig nur aus einem Kapitel stammt.

    uv run scripts/split_annotation.py --vorschlag data/studienheft/vorschlag.jsonl
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from promptner.data import load_jsonl, save_jsonl
from promptner.domain import Sentence

app = typer.Typer(add_completion=False)


def _blank(sent: Sentence) -> Sentence:
    """Derselbe Satz ohne Spans - die Vorlage fuer den blinden Block."""
    return Sentence(id=sent.id, tokens=sent.tokens, spans=[], source=sent.source)


@app.command()
def main(
    vorschlag: Annotated[Path, typer.Option(help="Vorbeschriftete Saetze")] = Path(
        "data/studienheft/vorschlag.jsonl"
    ),
    outdir: Annotated[Path, typer.Option(help="Zielverzeichnis")] = Path("data/studienheft"),
    names: Annotated[str, typer.Option(help="Zwei Namen, kommagetrennt")] = "joshua,alireza",
    overlap: Annotated[int, typer.Option(help="Saetze im gemeinsamen Block")] = 20,
) -> None:
    name_a, name_b = [n.strip() for n in names.split(",")]
    sentences = load_jsonl(vorschlag)
    if overlap >= len(sentences):
        raise typer.BadParameter(f"overlap {overlap} >= {len(sentences)} Saetze")

    # Gleichmaessig gestreute Auswahl statt Zufall: der Block deckt alle Kapitel ab.
    step = len(sentences) / overlap
    shared_idx = {int(i * step) for i in range(overlap)}
    shared = [_blank(sentences[i]) for i in sorted(shared_idx)]
    rest = [s for i, s in enumerate(sentences) if i not in shared_idx]

    # Alternierend teilen, damit beide Bloecke dieselbe thematische Streuung haben.
    part_a = rest[0::2]
    part_b = rest[1::2]

    shared_path = save_jsonl(shared, outdir / "gold_gemeinsam_VORLAGE.jsonl")
    a_path = save_jsonl(part_a, outdir / f"vorschlag_{name_a}.jsonl")
    b_path = save_jsonl(part_b, outdir / f"vorschlag_{name_b}.jsonl")

    typer.echo(f"-> {shared_path}  {len(shared)} Saetze, ohne Vorschlaege (beide, unabhaengig)")
    typer.echo(f"-> {a_path}  {len(part_a)} Saetze mit Vorschlaegen ({name_a})")
    typer.echo(f"-> {b_path}  {len(part_b)} Saetze mit Vorschlaegen ({name_b})")
    typer.echo(f"   je Person {len(shared) + len(part_a)} bzw. {len(shared) + len(part_b)} Saetze")


if __name__ == "__main__":
    app()
