"""Fuehrt einen ``RunSpec`` aus und schreibt Vorhersagen + Kennzahlen nach ``results/runs/<run_id>/``.

Ein Lauf ist wiederaufnehmbar: existiert ``summary.json``, wird er uebersprungen
(``resumed=True``). Damit lassen sich Experimentreihen nachts starten und nach
Abbruch fortsetzen, ohne Aufrufe zu wiederholen.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from promptner.config import get_logger
from promptner.data import load_by_name, load_jsonl
from promptner.domain import Sentence
from promptner.eval import evaluate
from promptner.experiments.spec import RunSpec
from promptner.llm.cache import ResponseCache
from promptner.llm.client import LlmClient
from promptner.pipeline import predict_many
from promptner.prompting import prompt_hash

log = get_logger("experiments.runner")

STUDIENHEFT_GOLD = Path("data/studienheft/gold.jsonl")


class RunRecord(BaseModel):
    """Flache Kennzahlen eines Laufs (eine Zeile in results/summary.csv)."""

    run_id: str
    experiment: str
    dataset: str
    split: str
    limit: int | None
    model: str
    use_definition: bool
    k_examples: int
    use_cot: bool
    use_candidates: bool
    output_format: str
    max_retries: int
    seed: int
    prompt_hash: str
    f1: float
    precision: float
    recall: float
    per_type_f1: str
    n_sentences: int
    parse_fail: int
    retries: int
    unmatched: int
    unknown_type: int
    elapsed_s: float
    n_calls: int
    timestamp: str
    resumed: bool = False


def load_sentences(dataset: str, split: str, limit: int | None) -> list[Sentence]:
    """Datensatz laden; ``studienheft`` kommt aus der annotierten JSONL (monkeypatch-Punkt)."""
    if dataset == "studienheft":
        sents = load_jsonl(STUDIENHEFT_GOLD)
        return sents[:limit] if limit else sents
    return load_by_name(dataset, split, limit=limit)  # type: ignore[arg-type]


def run_spec(
    spec: RunSpec,
    *,
    client: LlmClient,
    cache: ResponseCache | None,
    results_dir: str | Path,
    workers: int,
    on_progress=None,
) -> RunRecord:
    run_dir = Path(results_dir) / "runs" / spec.run_id
    summary_path = run_dir / "summary.json"
    if summary_path.is_file():
        rec = RunRecord.model_validate_json(summary_path.read_text(encoding="utf-8"))
        rec.resumed = True
        log.info("Lauf uebersprungen (bereits vorhanden): %s", spec.run_id)
        return rec

    sentences = load_sentences(spec.dataset, spec.split, spec.limit)
    calls_before = client.calls_made
    t0 = time.time()
    preds = predict_many(
        sentences,
        spec.config,
        client,
        workers=workers,
        cache=cache,
        model=spec.model,
        on_progress=on_progress,
    )
    elapsed = time.time() - t0
    result = evaluate(sentences, [p.spans for p in preds])

    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as fh:
        for sent, p in zip(sentences, preds, strict=True):
            row = {
                "sentence_id": sent.id,
                "tokens": sent.tokens,
                "gold": [s.model_dump() for s in sent.spans],
                "pred": [s.model_dump() for s in p.spans],
                "candidates": [c.model_dump() for c in p.candidates],
                "parse_ok": p.parse_ok,
                "retries": p.retries,
                "n_unmatched": p.n_unmatched,
                "n_unknown_type": p.n_unknown_type,
                "raw": p.raw,
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    cfg = spec.config
    rec = RunRecord(
        run_id=spec.run_id,
        experiment=spec.experiment,
        dataset=spec.dataset,
        split=spec.split,
        limit=spec.limit,
        model=spec.model,
        use_definition=cfg.use_definition,
        k_examples=cfg.k_examples,
        use_cot=cfg.use_cot,
        use_candidates=cfg.use_candidates,
        output_format=cfg.output_format,
        max_retries=cfg.max_retries,
        seed=cfg.seed,
        prompt_hash=prompt_hash(cfg),
        f1=result.f1,
        precision=result.precision,
        recall=result.recall,
        per_type_f1=json.dumps({k: round(v.f1, 4) for k, v in result.per_type.items()}),
        n_sentences=len(sentences),
        parse_fail=sum(not p.parse_ok for p in preds),
        retries=sum(p.retries for p in preds),
        unmatched=sum(p.n_unmatched for p in preds),
        unknown_type=sum(p.n_unknown_type for p in preds),
        elapsed_s=round(elapsed, 1),
        n_calls=client.calls_made - calls_before,
        timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    summary_path.write_text(rec.model_dump_json(indent=2), encoding="utf-8")
    log.info(
        "Lauf fertig: %s F1=%.4f (%d Saetze, %.0fs)", spec.run_id, rec.f1, rec.n_sentences, elapsed
    )
    return rec


def run_all(
    specs: list[RunSpec],
    *,
    client: LlmClient,
    cache: ResponseCache | None,
    results_dir: str | Path,
    workers: int,
    on_run_done=None,
) -> list[RunRecord]:
    records: list[RunRecord] = []
    for i, spec in enumerate(specs, start=1):
        log.info("Lauf %d/%d: %s", i, len(specs), spec.run_id)
        rec = run_spec(spec, client=client, cache=cache, results_dir=results_dir, workers=workers)
        records.append(rec)
        if on_run_done is not None:
            on_run_done(rec)
    return records
