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


@pytest.mark.unit
def test_variant_order_handles_composite_labels():
    """E8 hat Varianten wie 'k=0, text, retry=an' - die Zahl steht vor dem Komma."""
    from promptner.eval.plots import _variant_order

    order = [
        _variant_order(pd.Series({"variant": v}))
        for v in ("k=0, text, retry=an", "k=10", "p=5", "text, retry=an", "json, retry=aus")
    ]
    assert order[0] == 0.0
    assert order[1] == 10.0
    assert order[2] == 5.0
    assert order[3] == 0.0
    assert order[4] == 1.0


@pytest.mark.unit
def test_plots_do_not_crash_on_e8(tmp_path):
    """Regression: der Nachtlauf brach beim Zeichnen von E8 mit einem ValueError ab."""
    from promptner.eval.plots import plot_experiment

    rows = [
        {
            "experiment": "E8",
            "dataset": "conll2003",
            "model": "m",
            "variant": v,
            "f1_mean": 0.8,
            "f1_std": 0.01,
            "n": 3,
        }
        for v in ("k=0, text, retry=an", "text, retry=an", "json, retry=aus")
    ]
    out = plot_experiment(pd.DataFrame(rows), "E8", tmp_path / "E8.png")
    assert out.is_file()
