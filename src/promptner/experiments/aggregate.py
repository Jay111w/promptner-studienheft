"""Sammelt alle ``summary.json`` und aggregiert ueber Seeds (Mittelwert, Std, n)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

GROUP_KEYS = [
    "experiment",
    "dataset",
    "split",
    "limit",
    "model",
    "use_definition",
    "k_examples",
    "use_cot",
    "use_candidates",
    "output_format",
    "max_retries",
]
METRICS = [
    "f1",
    "precision",
    "recall",
    "parse_fail",
    "retries",
    "unmatched",
    "unknown_type",
    "elapsed_s",
]


def collect(results_dir: str | Path) -> pd.DataFrame:
    rows = []
    for path in sorted(Path(results_dir).glob("runs/*/summary.json")):
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    return pd.DataFrame(rows)


def variant_label(row: pd.Series) -> str:
    """Kurzbezeichnung der variierten Komponente(n) fuer Tabellen und Plots."""
    exp = row["experiment"]
    if exp == "E2":
        return str(row["dataset"])
    if exp == "E3":
        return str(row["model"])
    if exp == "E4":
        return "mit Definition" if row["use_definition"] else "ohne Definition"
    if exp == "E5":
        return "mit CoT" if row["use_cot"] else "ohne CoT"
    if exp == "E6":
        return f"k={row['k_examples']}"
    if exp == "E7":
        return "mit Kandidaten" if row["use_candidates"] else "nur Entitäten"
    if exp == "E8":
        return f"{row['output_format']}, retry={'an' if row['max_retries'] else 'aus'}"
    return f"{row['dataset']}/{row['model']}"


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    agg = df.groupby(GROUP_KEYS, dropna=False).agg(
        n=("seed", "count"),
        **{f"{m}_mean": (m, "mean") for m in METRICS},
        **{f"{m}_std": (m, "std") for m in METRICS},
    )
    agg = agg.reset_index()
    for m in METRICS:
        agg[f"{m}_std"] = agg[f"{m}_std"].fillna(0.0)
    agg["variant"] = agg.apply(variant_label, axis=1)
    return agg.sort_values(["experiment", "dataset", "model", "variant"]).reset_index(drop=True)


def write_summary(results_dir: str | Path) -> Path:
    out = Path(results_dir) / "summary.csv"
    summarize(collect(results_dir)).to_csv(out, index=False)
    return out
