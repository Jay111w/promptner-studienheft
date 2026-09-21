"""Unit-Tests fuer die Diagramme (Agg-Backend, PNG-Ausgabe)."""

import pandas as pd
import pytest

from promptner.eval.plots import plot_experiment


@pytest.mark.unit
def test_plot_experiment_writes_png(tmp_path):
    summary = pd.DataFrame(
        [
            {
                "experiment": "E6",
                "dataset": "conll2003",
                "model": "m",
                "variant": "k=0",
                "f1_mean": 0.3,
                "f1_std": 0.02,
                "n": 3,
            },
            {
                "experiment": "E6",
                "dataset": "conll2003",
                "model": "m",
                "variant": "k=5",
                "f1_mean": 0.6,
                "f1_std": 0.03,
                "n": 3,
            },
        ]
    )
    out = plot_experiment(summary, "E6", tmp_path / "e6.png")
    assert out.is_file() and out.stat().st_size > 1000


@pytest.mark.unit
def test_plot_unknown_experiment_raises(tmp_path):
    with pytest.raises(ValueError):
        plot_experiment(pd.DataFrame(), "E6", tmp_path / "x.png")
