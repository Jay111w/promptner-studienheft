"""Unit-Tests fuer RunSpec und die benannten Experimente."""

import pytest

from promptner.experiments.spec import build_experiment


@pytest.mark.unit
def test_e4_definition_ablation_three_seeds():
    specs = build_experiment("E4", models=["m"], seeds=[1, 2, 3], limit=50)
    assert len(specs) == 6
    assert {s.config.use_definition for s in specs} == {True, False}
    assert {s.config.seed for s in specs} == {1, 2, 3}
    assert all(
        s.experiment == "E4" and s.dataset == "conll2003" and s.split == "validation" for s in specs
    )
    assert len({s.run_id for s in specs}) == 6


@pytest.mark.unit
def test_e6_k_and_e8_format_retry():
    e6 = build_experiment("E6", models=["m"], seeds=[1], limit=10)
    assert sorted(s.config.k_examples for s in e6) == [0, 2, 5, 10]
    e8 = build_experiment("E8", models=["m"], seeds=[1], limit=10)
    assert {(s.config.output_format, s.config.max_retries) for s in e8} == {
        ("text", 1),
        ("text", 0),
        ("json", 1),
        ("json", 0),
    }


@pytest.mark.unit
def test_e3_models_and_e2_datasets():
    e3 = build_experiment("E3", models=["a", "b", "c"], seeds=[1, 2], limit=10)
    assert len(e3) == 6 and {s.model for s in e3} == {"a", "b", "c"}
    e2 = build_experiment("E2", models=["m"], seeds=[1], limit=10)
    assert {s.dataset for s in e2} == {"conll2003", "germeval14"}


@pytest.mark.unit
def test_run_id_contains_all_dimensions():
    (spec,) = build_experiment("E4", models=["llama-3.1-8b"], seeds=[7], limit=5)[:1]
    assert spec.run_id.startswith("E4__conll2003-validation-5__llama-3.1-8b__conll2003_def")
    assert spec.run_id.endswith("_s7_p2")


@pytest.mark.unit
def test_unknown_experiment():
    with pytest.raises(ValueError):
        build_experiment("E99", models=["m"], seeds=[1], limit=1)
