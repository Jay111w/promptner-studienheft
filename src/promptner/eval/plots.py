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
}


def _variant_order(row: pd.Series) -> float:
    """Numerische Reihenfolge fuer k=...; sonst 'mit' vor 'ohne', Rest alphabetisch."""
    v = str(row["variant"])
    if v.startswith("k="):
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
