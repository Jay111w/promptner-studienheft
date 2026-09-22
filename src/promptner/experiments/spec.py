"""Beschreibung einzelner Laeufe und der benannten Experimente E2-E8 (CODING_PLAN §9).

Ein ``RunSpec`` ist vollstaendig bestimmt durch Datensatz, Split, Limit, Modell
und PromptConfig; die ``run_id`` ist der Ordnername unter ``results/runs/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from promptner.domain import PromptConfig

DEFAULT_DATASET = "conll2003"
DEFAULT_SPLIT = "validation"


@dataclass(frozen=True)
class RunSpec:
    experiment: str
    dataset: str
    split: str
    limit: int | None
    model: str
    config: PromptConfig

    @property
    def run_id(self) -> str:
        n = self.limit if self.limit is not None else "all"
        return f"{self.experiment}__{self.dataset}-{self.split}-{n}__{self.model}__{self.config.short_name()}"


def _specs(
    experiment: str,
    variants: list[dict],
    *,
    models: list[str],
    seeds: list[int],
    limit: int | None,
    dataset=None,
    split=DEFAULT_SPLIT,
) -> list[RunSpec]:
    out: list[RunSpec] = []
    for model in models:
        for variant in variants:
            ds = (
                variant.pop("dataset", dataset or DEFAULT_DATASET)
                if "dataset" in variant
                else (dataset or DEFAULT_DATASET)
            )
            for seed in seeds:
                cfg = PromptConfig(dataset=ds, seed=seed, **variant)
                out.append(RunSpec(experiment, ds, split, limit, model, cfg))
    return out


def build_experiment(
    name: str,
    *,
    models: list[str],
    seeds: list[int],
    limit: int | None,
    datasets: list[str] | None = None,
    split: str = DEFAULT_SPLIT,
    studienheft_gold: Path | None = None,
) -> list[RunSpec]:
    """Erzeugt alle Laeufe eines benannten Experiments."""
    if name == "E2":
        ds_list = datasets or ["conll2003", "germeval14"]
        if (
            studienheft_gold is not None
            and Path(studienheft_gold).is_file()
            and "studienheft" not in ds_list
        ):
            ds_list = [*ds_list, "studienheft"]
        return [
            s
            for ds in ds_list
            for s in _specs(
                "E2", [{}], models=models, seeds=seeds, limit=limit, dataset=ds, split=split
            )
        ]
    if name == "E3":
        return _specs("E3", [{}], models=models, seeds=seeds, limit=limit, split=split)
    if name == "E4":
        return _specs(
            "E4",
            [{"use_definition": True}, {"use_definition": False}],
            models=models,
            seeds=seeds,
            limit=limit,
            split=split,
        )
    if name == "E5":
        return _specs(
            "E5",
            [{"use_cot": True}, {"use_cot": False}],
            models=models,
            seeds=seeds,
            limit=limit,
            split=split,
        )
    if name == "E6":
        return _specs(
            "E6",
            [{"k_examples": k} for k in (0, 2, 5, 10)],
            models=models,
            seeds=seeds,
            limit=limit,
            split=split,
        )
    if name == "E7":
        return _specs(
            "E7",
            [{"use_candidates": True}, {"use_candidates": False}],
            models=models,
            seeds=seeds,
            limit=limit,
            split=split,
        )
    if name == "E8":
        # Ausgabeformat x Retry. Bei k=5 bricht das Format nie, der Retry greift also nicht -
        # deshalb zusaetzlich k=0, wo jeder Absatz beim ersten Versuch scheitert (siehe E6).
        variants = [
            {"output_format": f, "max_retries": r} for f in ("text", "json") for r in (1, 0)
        ]
        variants += [{"k_examples": 0, "output_format": "text", "max_retries": r} for r in (1, 0)]
        return _specs("E8", variants, models=models, seeds=seeds, limit=limit, split=split)
    if name == "E10":
        # Zusatz: Saetze je Aufruf ("Paragraph"), Budget vs. Recall
        return _specs(
            "E10",
            [{"paragraph_size": n} for n in (1, 2, 3, 5)],
            models=models,
            seeds=seeds,
            limit=limit,
            split=split,
        )
    if name == "E1":
        ds_list = datasets or ["conll2003", "germeval14"]
        return [
            s
            for ds in ds_list
            for s in _specs(
                "E1", [{}], models=models, seeds=seeds, limit=limit, dataset=ds, split="test"
            )
        ]
    raise ValueError(f"Unbekanntes Experiment: {name!r}. Bekannt: E1-E8, E10")
