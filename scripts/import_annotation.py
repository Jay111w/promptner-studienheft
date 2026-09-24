"""Den Rueckweg aus der Annotations-Oberflaeche gehen: JSON-Ausgabe zu JSONL.

Die Oberflaeche gibt je Annotator eine Datei ``annotation_<name>.json`` heraus (oder denselben
Text ueber die Zwischenablage). Hier wird daraus, was der Rest des Projekts liest:

``gold_gemeinsam_<name>.jsonl``
    Der ueberlappende Block. Nur dieser geht in ``promptner agreement`` ein.

``gold_<name>.jsonl``
    Der persoenliche Block, also der Teil, der spaeter zum gemeinsamen Gold zusammenwaechst.

Die Tokens der Ausgabe werden gegen die Vorlage geprueft. Ein Text, der durch einen Messenger
gelaufen ist, verliert schnell ein Zeichen; das faellt dann hier auf und nicht erst in der
Auswertung.

    uv run scripts/import_annotation.py --datei ../annotation_alireza.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from promptner.data import load_jsonl, save_jsonl
from promptner.domain import Sentence, Span

app = typer.Typer(add_completion=False)

SOURCE = "studienheft"


def _vorlage(outdir: Path, name: str) -> dict[str, list[str]]:
    """Tokens je Satz-ID aus dem gemeinsamen Block und dem persoenlichen Block des Namens."""
    tokens: dict[str, list[str]] = {}
    for pfad in (outdir / "gold_gemeinsam_VORLAGE.jsonl", outdir / f"vorschlag_{name}.jsonl"):
        for satz in load_jsonl(pfad):
            tokens[satz.id] = satz.tokens
    return tokens


@app.command()
def main(
    datei: Annotated[Path, typer.Option(help="JSON-Ausgabe der Oberflaeche")],
    outdir: Annotated[Path, typer.Option(help="Zielverzeichnis")] = Path("data/studienheft"),
) -> None:
    rohdaten = json.loads(datei.read_text(encoding="utf-8"))
    name = rohdaten["annotator"]
    vorlage = _vorlage(outdir, name)

    bloecke: dict[str, list[Sentence]] = {"gemeinsam": [], "persoenlich": []}
    offen: list[str] = []
    for eintrag in rohdaten["saetze"]:
        sid = eintrag["id"]
        if sid not in vorlage:
            raise typer.BadParameter(f"{sid} steht nicht in der Vorlage fuer {name}")
        if vorlage[sid] != eintrag["tokens"]:
            raise typer.BadParameter(
                f"{sid}: Tokens weichen von der Vorlage ab - die Ausgabe ist unterwegs beschaedigt"
            )
        if not eintrag["erledigt"]:
            offen.append(sid)
        bloecke[eintrag["block"]].append(
            Sentence(
                id=sid,
                tokens=eintrag["tokens"],
                spans=[Span(**sp) for sp in eintrag["spans"]],
                source=SOURCE,
            )
        )

    gemeinsam = save_jsonl(bloecke["gemeinsam"], outdir / f"gold_gemeinsam_{name}.jsonl")
    persoenlich = save_jsonl(bloecke["persoenlich"], outdir / f"gold_{name}.jsonl")

    n_spans = sum(len(s.spans) for block in bloecke.values() for s in block)
    typer.echo(f"-> {gemeinsam}  {len(bloecke['gemeinsam'])} Saetze (Uebereinstimmungsblock)")
    typer.echo(f"-> {persoenlich}  {len(bloecke['persoenlich'])} Saetze (persoenlicher Block)")
    typer.echo(f"   {n_spans} Spans insgesamt")
    if offen:
        typer.echo(
            f"   ACHTUNG {len(offen)} Saetze nicht als erledigt markiert: {', '.join(offen)}"
        )


if __name__ == "__main__":
    app()
