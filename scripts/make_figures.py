"""Erzeugt die selbst gezeichneten Abbildungen des Berichts als SVG, PDF und PNG.

    uv run scripts/make_figures.py            # -> results/figures/A1.{svg,pdf,png} usw.

A1 Prompt-Aufbau · A2 Pipeline · A5 Absatzgroesse vs. F1 (aus results/summary.csv).
A3 (Ablationsbalken) und A4 (Verwechslungsmatrix) entstehen aus den Daten:
``promptner plots`` bzw. ``promptner errors``.

Schwarz auf Weiss mit einem Akzentton, damit die Abbildungen auch im Schwarzweissdruck
funktionieren; Schriftgroessen sind fuer die Darstellung auf halber Seitenbreite gewaehlt.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

ACCENT = "#0e7c7b"
INK = "#1b2430"
MUTED = "#6f7b87"
FONT = "Helvetica, Arial, sans-serif"
MONO = "'IBM Plex Mono', Menlo, monospace"

# PyMuPDF rendert weder <marker> noch stroke-dasharray - Pfeilspitzen und Striche
# werden daher als Polygone bzw. Einzelsegmente gezeichnet.
_HEAD = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
    '<rect width="{w}" height="{h}" fill="#ffffff"/>'
)


def _box(x, y, w, h, *, accent=False, fill="none"):
    stroke = ACCENT if accent else INK
    width = 1.6 if accent else 1.0
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width}"/>'
    )


def _t(x, y, s, *, size=11, anchor="start", color=INK, weight="normal", mono=False):
    fam = MONO if mono else FONT
    return (
        f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{color}" '
        f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>'
    )


def _head(x, y, dx, dy, size=5.0):
    """Pfeilspitze als Polygon am Punkt (x, y), Richtung (dx, dy) normiert."""
    import math

    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    x1, y1 = x - ux * size * 1.8 + px * size * 0.7, y - uy * size * 1.8 + py * size * 0.7
    x2, y2 = x - ux * size * 1.8 - px * size * 0.7, y - uy * size * 1.8 - py * size * 0.7
    return f'<polygon points="{x},{y} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" fill="{INK}"/>'


def _arrow(x1, y1, x2, y2, dashed=False):
    parts = []
    if dashed:
        import math

        n = math.hypot(x2 - x1, y2 - y1)
        steps = max(1, int(n // 6))
        for i in range(steps):
            a, b = i / steps, min(1.0, (i + 0.55) / steps)
            parts.append(
                f'<line x1="{x1 + (x2 - x1) * a:.1f}" y1="{y1 + (y2 - y1) * a:.1f}" '
                f'x2="{x1 + (x2 - x1) * b:.1f}" y2="{y1 + (y2 - y1) * b:.1f}" '
                f'stroke="{INK}" stroke-width="1"/>'
            )
    else:
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1"/>'
        )
    parts.append(_head(x2, y2, x2 - x1, y2 - y1))
    return "".join(parts)


def figure_a1() -> tuple[str, int, int]:
    """Der PromptNER-Prompt: vier Bausteine und die Ablation, die jeden entfernt."""
    w, h = 720, 400
    p = [_HEAD.format(w=w, h=h)]
    # Bloecke
    p += [_box(14, 14, 470, 62, accent=True)]
    p += [_t(26, 32, "Defn:", size=12, weight="600")]
    p += [
        _t(
            26,
            48,
            "An entity is a person (person), an organisation (organisation) such as a",
            size=10,
            mono=True,
        )
    ]
    p += [
        _t(
            26,
            64,
            "company, institution, … Dates, numbers, job titles are not entities.",
            size=10,
            mono=True,
        )
    ]
    p += [_box(14, 86, 470, 62)]
    p += [_t(26, 104, "Q:", size=12, weight="600")]
    p += [
        _t(
            26,
            122,
            "Given the paragraph below, identify a list of possible entities and for each",
            size=10,
            mono=True,
        )
    ]
    p += [_t(26, 138, "entry explain why it either is or is not an entity:", size=10, mono=True)]
    p += [_box(14, 158, 470, 152, accent=True)]
    p += [_t(26, 176, "Beispiel 1 von k", size=12, weight="600")]
    p += [
        _t(
            26,
            196,
            "Paragraph: EU rejects German call to boycott British lamb .",
            size=10,
            mono=True,
        )
    ]
    p += [_t(26, 214, "Answer:", size=10, mono=True)]
    p += [_t(26, 232, "1. EU | True | as the European Union is a political", size=10, mono=True)]
    p += [_t(26, 248, "   organisation (organisation)", size=10, mono=True)]
    p += [
        _t(26, 266, "2. German | True | as it is a nationality (miscellaneous)", size=10, mono=True)
    ]
    p += [
        _t(
            26,
            282,
            "3. lamb | False | as it is a common noun, not a named entity",
            size=10,
            mono=True,
        )
    ]
    p += [_t(26, 300, "… Beispiele 2 bis k …", size=10, color=MUTED, mono=True)]
    p += [_box(14, 320, 470, 62)]
    p += [_t(26, 338, "Zielabsatz", size=12, weight="600")]
    p += [_t(26, 356, "Paragraph: At the Oval , Surrey captain Chris Lewis … ", size=10, mono=True)]
    p += [_t(26, 374, "Answer:", size=10, mono=True)]
    # Ablationen rechts
    for y, label in (
        (45, "E4 ohne Definition"),
        (234, "E6 k = 0 / 2 / 5 / 10"),
        (351, "E10 1–5 Sätze"),
    ):
        p += [f'<line x1="484" y1="{y}" x2="512" y2="{y}" stroke="{INK}" stroke-width="1"/>']
        p += [_t(518, y + 4, label, size=11, weight="600")]
    p += [_t(518, 256, "E5 ohne Begründung", size=11, weight="600")]
    p += [_t(518, 276, "E7 ohne False-Zeilen", size=11, weight="600")]
    p += [_t(518, 118, "bleibt immer", size=10, color=MUTED)]
    p.append("</svg>")
    return "".join(p), w, h


def figure_a2() -> tuple[str, int, int]:
    """Pipeline: Absatz zu Spans, mit den beiden Zaehlern."""
    w, h = 720, 250
    p = [_HEAD.format(w=w, h=h)]
    boxes = [
        (14, "n Sätze", "= 1 Absatz", False),
        (150, "Prompt", "Defn + Q + k Bsp.", False),
        (286, "Sprachmodell", "1 API-Aufruf", True),
        (422, "Parser", "Zeilen → Kandidaten", False),
        (558, "Alignment", "im Satz suchen", False),
    ]
    for x, a, b, acc in boxes:
        p += [_box(x, 20, 128, 52, accent=acc)]
        p += [_t(x + 64, 42, a, size=11.5, anchor="middle", weight="600")]
        p += [_t(x + 64, 60, b, size=10, anchor="middle", color=MUTED)]
        if x < 558:
            p += [_arrow(x + 128, 46, x + 146, 46)]
    # Zaehler
    p += [_arrow(486, 72, 486, 100, dashed=True)]
    p += [_t(486, 116, "Format kaputt? 1 Retry,", size=10, anchor="middle", color=MUTED)]
    p += [_t(486, 130, "sonst Format-Fehler (E8)", size=10, anchor="middle", color=MUTED)]
    p += [_arrow(622, 72, 622, 100, dashed=True)]
    p += [_t(622, 116, "nicht im Text? verworfen,", size=10, anchor="middle", color=MUTED)]
    p += [_t(622, 130, "als halluziniert gezählt", size=10, anchor="middle", color=MUTED)]
    # Rueckweg
    p += [
        f'<path d="M686,46 L700,46 L700,196 L558,196" fill="none" stroke="{INK}" stroke-width="1"/>'
        + _head(558, 196, -1, 0)
    ]
    p += [_box(420, 170, 132, 52)]
    p += [_t(486, 192, "Spans je Satz", size=11.5, anchor="middle", weight="600")]
    p += [_t(486, 210, "Offsets zurück", size=10, anchor="middle", color=MUTED)]
    p += [_arrow(420, 196, 402, 196)]
    p += [_box(258, 170, 142, 52, fill="#eef5f4")]
    p += [_t(329, 192, "Vergleich mit Gold", size=11.5, anchor="middle", weight="600")]
    p += [_t(329, 210, "seqeval: P · R · F1", size=10, anchor="middle")]
    p += [_arrow(258, 196, 240, 196)]
    p += [_box(100, 170, 138, 52)]
    p += [_t(169, 192, "Fehleranalyse", size=11.5, anchor="middle", weight="600")]
    p += [_t(169, 210, "Matrix · Beispiele", size=10, anchor="middle", color=MUTED)]
    p.append("</svg>")
    return "".join(p), w, h


def _write(name: str, svg: str, out_dir: Path) -> list[Path]:
    import pymupdf

    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"{name}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    doc = pymupdf.open(str(svg_path))
    pdf_path = out_dir / f"{name}.pdf"
    pdf_path.write_bytes(doc.convert_to_pdf())
    png_path = out_dir / f"{name}.png"
    doc[0].get_pixmap(dpi=300).save(str(png_path))
    return [svg_path, pdf_path, png_path]


def figure_a5(out_dir: Path) -> list[Path]:
    """Absatzgroesse vs. F1 und Aufrufe (E10), aus results/summary.csv."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    df = pd.read_csv("results/summary.csv")
    e10 = df[df["experiment"] == "E10"].copy()
    if e10.empty:
        return []
    e10["p"] = e10["variant"].str.removeprefix("p=").astype(int)
    e10 = e10.sort_values("p")
    calls = [-(-100 // p) for p in e10["p"]]  # aufrunden: der letzte Absatz ist oft kuerzer

    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    ax.plot(
        e10["p"], e10["f1_mean"], marker="o", color=ACCENT, linewidth=2, markersize=7, label="F1"
    )
    for x, y in zip(e10["p"], e10["f1_mean"], strict=True):
        ax.annotate(
            f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9
        )
    ax.set_xlabel("Sätze je Aufruf")
    ax.set_ylabel("F1 (CoNLL-Dev-100, Llama 8B)")
    ax.set_xticks(list(e10["p"]))
    ax.set_ylim(0.68, 0.87)
    ax.grid(axis="y", color="#e5e9ee", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(list(e10["p"]))
    ax2.set_xticklabels([f"{c}" for c in calls])
    ax2.set_xlabel("API-Aufrufe für 100 Sätze", color=MUTED, fontsize=9)
    ax2.tick_params(colors=MUTED, labelsize=9)
    for s in ("top", "right", "left"):
        ax2.spines[s].set_visible(False)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("pdf", "png", "svg"):
        p = out_dir / f"A5.{ext}"
        fig.savefig(p, dpi=300)
        paths.append(p)
    plt.close(fig)
    return paths


app = typer.Typer(add_completion=False)


@app.command()
def main(out: Annotated[str, typer.Option(help="Zielordner")] = "results/figures") -> None:
    out_dir = Path(out)
    written: list[Path] = []
    for name, fn in (("A1", figure_a1), ("A2", figure_a2)):
        svg, _, _ = fn()
        written += _write(name, svg, out_dir)
    written += figure_a5(out_dir)
    for p in written:
        typer.echo(f"-> {p}")


if __name__ == "__main__":
    app()
