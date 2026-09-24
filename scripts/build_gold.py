"""Aus den beiden Annotationen das Gold fuer E2 bauen - ohne weitere Klickrunde.

Der Weg:

1. **Richtlinien durchsetzen** (``promptner.data.normalize``). Beide Annotationen laufen durch
   dieselben Regeln, die in ``data/studienheft/ANNOTATION.md`` vorab festgelegt waren.
2. **Gemeinsamen Block zusammenfuehren.** Nach Schritt 1 ist das Label je Oberflaeche eindeutig,
   Typkonflikte koennen also nicht mehr auftreten. Bleibt die Abdeckung: ein Span, den nur einer
   markiert hat, kommt ins Gold, denn die Fehleranalyse zeigt Auslassungen als den haeufigsten
   Fall, nicht Erfindungen. Ueberlappen zwei Lesarten, gewinnt die laengere.
3. **Persoenliche Bloecke anhaengen**, normalisiert, ohne Zusammenfuehrung - sie ueberschneiden
   sich nicht.

Es werden **keine Saetze entfernt**, auch keine Tabellen- und Fussnotenreste. Leere Fragmente
wegzuwerfen wuerde die gemessene Praezision der Modelle verbessern, ohne dass sie besser waeren:
gerade dort zeigt sich, ob ein Modell Entitaeten erfindet.

    uv run scripts/build_gold.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from promptner.data import load_jsonl, save_jsonl
from promptner.data.normalize import (
    Protokoll,
    normalisiere,
    normalisiere_satz,
    ohne_ueberlappung,
)
from promptner.domain import Sentence

app = typer.Typer(add_completion=False)


def _vereine(a: Sentence, b: Sentence) -> Sentence:
    """Die Lesarten beider Annotatoren zu einem Satz zusammenfuehren."""
    return Sentence(
        id=a.id,
        tokens=a.tokens,
        spans=ohne_ueberlappung(list(a.spans) + list(b.spans)),
        source=a.source,
    )


def _zeilen(titel: str, paare: list[tuple[str, str]]) -> list[str]:
    from collections import Counter

    zaehler = Counter(paare)
    zeilen = [f"### {titel} ({sum(zaehler.values())})", ""]
    if not zaehler:
        return zeilen + ["-", ""]
    zeilen.append("| n | von | nach |")
    zeilen.append("|---|---|---|")
    for (links, rechts), n in sorted(zaehler.items(), key=lambda kv: (-kv[1], kv[0][0])):
        zeilen.append(f"| {n} | `{links}` | `{rechts}` |")
    return zeilen + [""]


def _protokoll_md(name: str, vorher: int, nachher: int, p: Protokoll) -> list[str]:
    zeilen = [
        f"## {name}",
        "",
        f"Spans vorher **{vorher}**, nach Durchsetzung der Richtlinien **{nachher}**.",
        "",
    ]
    zeilen += _zeilen("Grenzen korrigiert oder Typ aus dem Lexikon gesetzt", p.getrimmt)
    zeilen += _zeilen("Als Gattungsbegriff verworfen", list(p.verworfen))
    return zeilen


@app.command()
def main(
    datadir: Annotated[Path, typer.Option(help="Verzeichnis der Annotationen")] = Path(
        "data/studienheft"
    ),
    names: Annotated[str, typer.Option(help="Zwei Namen, kommagetrennt")] = "joshua,alireza",
    bericht: Annotated[Path, typer.Option(help="Protokoll der Normalisierung")] = Path(
        "results/richtlinien-normalisierung.md"
    ),
) -> None:
    name_a, name_b = [n.strip() for n in names.split(",")]
    zeilen = [
        "# Richtlinien maschinell durchgesetzt",
        "",
        "Erzeugt von `scripts/build_gold.py`. Die Regeln stehen in",
        "`src/promptner/data/normalize.py`, die Richtlinien in `data/studienheft/ANNOTATION.md`.",
        "",
    ]
    gold: list[Sentence] = []

    # Gemeinsamer Block: normalisieren, dann zusammenfuehren.
    gemeinsam: dict[str, list[Sentence]] = {}
    for name in (name_a, name_b):
        roh = load_jsonl(datadir / f"gold_gemeinsam_{name}.jsonl")
        neu, p = normalisiere(roh)
        save_jsonl(neu, datadir / f"gold_gemeinsam_{name}_richtlinien.jsonl")
        gemeinsam[name] = neu
        zeilen += _protokoll_md(
            f"{name}, gemeinsamer Block",
            sum(len(s.spans) for s in roh),
            sum(len(s.spans) for s in neu),
            p,
        )

    spans_a = {s.id: set(s.spans) for s in gemeinsam[name_a]}
    spans_b = {s.id: set(s.spans) for s in gemeinsam[name_b]}
    vereint = [
        _vereine(s, next(t for t in gemeinsam[name_b] if t.id == s.id)) for s in gemeinsam[name_a]
    ]
    gold += vereint

    nur_a = sum(len(spans_a[sid] - spans_b[sid]) for sid in spans_a)
    nur_b = sum(len(spans_b[sid] - spans_a[sid]) for sid in spans_b)
    beide = sum(len(spans_a[sid] & spans_b[sid]) for sid in spans_a)

    # Persoenliche Bloecke: nur normalisieren.
    for name in (name_a, name_b):
        roh = load_jsonl(datadir / f"gold_{name}.jsonl")
        neu = [normalisiere_satz(s) for s in roh]
        save_jsonl(neu, datadir / f"gold_{name}_richtlinien.jsonl")
        gold += neu

    gold.sort(key=lambda s: int(s.id.rsplit("-", 1)[1]))
    ziel = save_jsonl(gold, datadir / "gold.jsonl")

    n_spans = sum(len(s.spans) for s in gold)
    zeilen += [
        "## Gold",
        "",
        f"- Saetze: **{len(gold)}** (keiner entfernt, auch keine Fragmente)",
        f"- Spans: **{n_spans}**",
        f"- Gemeinsamer Block zusammengefuehrt: {sum(len(s.spans) for s in vereint)} Spans, "
        f"davon von beiden gesehen {beide}, nur von {name_a} {nur_a}, nur von {name_b} {nur_b}",
        "",
    ]
    bericht.parent.mkdir(parents=True, exist_ok=True)
    bericht.write_text("\n".join(zeilen) + "\n", encoding="utf-8")

    typer.echo(f"-> {ziel}  {len(gold)} Saetze, {n_spans} Spans")
    typer.echo(f"-> {bericht}")


if __name__ == "__main__":
    app()
