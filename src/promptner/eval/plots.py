"""Diagramme fuer den Bericht: Balken mit Std-Fehlerbalken je Experiment (Agg, PNG)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

_TITLES = {
    "E1": "Headline: PromptNER auf den Test-Sets",
    "E2": "Datensatz / Sprache",
    "E3": "Modell-Tausch",
    "E4": "Ablation: Definition",
    "E5": "Ablation: Chain-of-Thought",
    "E6": "Ablation: Anzahl Few-Shot-Beispiele",
    "E7": "Ablation: Kandidatenliste",
    "E8": "Ausgabeformat und Retry",
    "E10": "Zusatz: Sätze je Aufruf (Absatzgröße)",
}


def _variant_order(row: pd.Series) -> float:
    """Numerische Reihenfolge fuer k=...; sonst 'mit' vor 'ohne', Rest alphabetisch."""
    v = str(row["variant"])
    if v.startswith("k=") or v.startswith("p="):
        return float(v[2:])
    if v.startswith("mit") or v.startswith("text"):
        return 0.0
    if v.startswith("ohne") or v.startswith("nur") or v.startswith("json"):
        return 1.0
    return 2.0


def plot_experiment(summary: pd.DataFrame, experiment: str, out: str | Path) -> Path:
    sub = summary[summary["experiment"] == experiment] if not summary.empty else summary
    if sub.empty:
        raise ValueError(f"Keine Ergebnisse fuer {experiment}")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    groups = sub.groupby("model") if experiment != "E3" else [(None, sub)]
    n_groups = len(groups) if experiment != "E3" else 1
    fig, axes = plt.subplots(1, n_groups, figsize=(4.5 * n_groups + 1, 3.8), squeeze=False)
    for ax, (model, part) in zip(axes[0], groups, strict=False):
        part = part.assign(_order=part.apply(_variant_order, axis=1)).sort_values(
            ["_order", "variant"]
        )
        x = range(len(part))
        ax.bar(
            x,
            part["f1_mean"] * 100,
            yerr=part["f1_std"] * 100,
            capsize=4,
            color="#0e7c7b",
            alpha=0.9,
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(part["variant"], rotation=20, ha="right")
        ax.set_ylabel("Micro-F1 (%)")
        ax.set_ylim(0, 100)
        title = _TITLES.get(experiment, experiment)
        ax.set_title(f"{title}\n{model}" if model else title, fontsize=10)
        for xi, (m, sd, n) in enumerate(
            zip(part["f1_mean"], part["f1_std"], part["n"], strict=True)
        ):
            ax.text(
                xi,
                (m + sd) * 100 + 1.5,
                f"{m * 100:.1f}\n(n={n})",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_confusion(
    matrix: dict[tuple[str, str], int], labels: list[str], out: str | Path, *, title: str = ""
) -> Path:
    """Verwechslungsmatrix Gold x Pred als Heatmap: ein Farbton hell->dunkel, Zahl je Zelle.

    ``labels`` ohne "O"; die Spalte/Zeile "O" (kein Span) wird angehaengt. Die Diagonale
    (korrekt) wird durch die Zahl sichtbar, nicht durch eine zweite Farbe.
    """
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    cols = [*labels, "O"]
    data = np.array([[matrix.get((g, p), 0) for p in cols] for g in cols], dtype=float)
    data[-1, -1] = np.nan  # O->O ist nicht definiert
    cmap = LinearSegmentedColormap.from_list("teal", ["#f2f7f7", "#0e7c7b"])
    cmap.set_bad("#ffffff")
    vmax = max(1.0, np.nanmax(data))

    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=vmax)
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(cols)), cols)
    ax.set_xlabel("Vorhersage (O = kein Span)")
    ax.set_ylabel("Gold")
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(cols)), minor=True)
    ax.set_yticks(np.arange(-0.5, len(cols)), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=2)
    ax.tick_params(which="both", length=0)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = data[i, j]
            if np.isnan(v):
                ax.text(j, i, "–", ha="center", va="center", color="#6f7b87", fontsize=10)
                continue
            ink = "#ffffff" if v > 0.55 * vmax else "#1b2430"
            ax.text(j, i, f"{int(v)}", ha="center", va="center", color=ink, fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Spans")
    if title:
        ax.set_title(title, fontsize=9, pad=36, loc="left", color="#6f7b87")
    fig.tight_layout()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out
