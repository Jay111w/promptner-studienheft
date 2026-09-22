"""BERT-Baseline fuer CoNLL-2003: Fine-Tuning mit Linear-Kopf, bewertet mit derselben seqeval-
Funktion wie PromptNER und abgelegt als normaler Lauf unter ``results/runs/``.

torch/transformers werden erst in ``train_and_evaluate`` importiert (Extra ``bert``), damit das
Paket ohne sie importierbar bleibt. Die reinen Hilfsfunktionen sind ohne Modell testbar.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from promptner.config import get_logger
from promptner.data.bio import bio_to_spans, spans_to_bio
from promptner.data.loaders import load_by_name
from promptner.domain import LABELS_CONLL, Sentence
from promptner.eval.metrics import evaluate

log = get_logger("baseline.bert")

LABELS_CONLL_BIO: tuple[str, ...] = ("O",) + tuple(
    f"{p}-{t}" for t in LABELS_CONLL for p in ("B", "I")
)
IGNORE = -100


def align_labels(word_ids: list[int | None], labels: list[int]) -> list[int]:
    """Wort-Labels auf Subwords: erstes Subword traegt das Label, Rest und Sonder-Tokens -100."""
    out: list[int] = []
    prev: int | None = None
    for wid in word_ids:
        if wid is None or wid == prev:
            out.append(IGNORE)
        else:
            out.append(labels[wid])
        prev = wid if wid is not None else prev
    return out


def first_subword_predictions(
    word_ids: list[int | None], pred_ids: list[int], n_words: int
) -> list[int]:
    """Je Wort die Vorhersage seines ersten Subwords; Woerter ohne Subword (abgeschnitten) -> O."""
    out = [0] * n_words
    seen: set[int] = set()
    for wid, pid in zip(word_ids, pred_ids, strict=False):
        if wid is None or wid in seen or wid >= n_words:
            continue
        seen.add(wid)
        out[wid] = pid
    return out


def label_ids_to_bio(ids: list[int]) -> list[str]:
    return [LABELS_CONLL_BIO[i] for i in ids]


@dataclass
class TrainConfig:
    model_name: str = "bert-base-cased"
    epochs: int = 3
    batch_size: int = 16
    lr: float = 5e-5
    warmup_ratio: float = 0.1
    max_length: int = 128
    seed: int = 1
    train_limit: int | None = None
    eval_split: str = "validation"
    eval_limit: int | None = 150


def _device():
    import torch

    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _encode(tokenizer: Any, sentences: list[Sentence], max_length: int) -> list[dict]:
    rows = []
    for s in sentences:
        tags = spans_to_bio(s.spans, len(s.tokens))
        enc = tokenizer(s.tokens, is_split_into_words=True, truncation=True, max_length=max_length)
        labels = [LABELS_CONLL_BIO.index(t) for t in tags]
        enc["labels"] = align_labels(enc.word_ids(), labels)
        rows.append(dict(enc))
    return rows


def train_and_evaluate(cfg: TrainConfig, results_dir: str | Path = "results") -> dict:
    """Trainiert auf CoNLL-Train, bewertet auf ``cfg.eval_split`` und schreibt den Lauf."""
    import torch
    from torch.utils.data import DataLoader
    from transformers import (
        AutoModelForTokenClassification,
        AutoTokenizer,
        DataCollatorForTokenClassification,
        get_linear_schedule_with_warmup,
    )

    torch.manual_seed(cfg.seed)
    device = _device()
    log.info("BERT-Baseline: %s auf %s, %d Epochen", cfg.model_name, device, cfg.epochs)

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    train = load_by_name("conll2003", "train", limit=cfg.train_limit)
    eval_sents = load_by_name("conll2003", cfg.eval_split, limit=cfg.eval_limit)  # type: ignore[arg-type]
    collator = DataCollatorForTokenClassification(tokenizer)
    train_loader = DataLoader(
        _encode(tokenizer, train, cfg.max_length),
        batch_size=cfg.batch_size,
        shuffle=True,
        collate_fn=collator,
    )
    model = AutoModelForTokenClassification.from_pretrained(
        cfg.model_name,
        num_labels=len(LABELS_CONLL_BIO),
        id2label=dict(enumerate(LABELS_CONLL_BIO)),
        label2id={lbl: i for i, lbl in enumerate(LABELS_CONLL_BIO)},
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
    total = len(train_loader) * cfg.epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, int(cfg.warmup_ratio * total), total)

    t0 = time.time()
    model.train()
    step = 0
    for epoch in range(cfg.epochs):
        running = 0.0
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            loss = model(**batch).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            running += loss.item()
            step += 1
            if step % 100 == 0:
                log.info(
                    "Epoche %d, Schritt %d/%d, Loss %.4f", epoch + 1, step, total, running / 100
                )
                running = 0.0
    train_s = time.time() - t0

    # Vorhersage: erstes Subword je Wort -> BIO -> Spans
    model.eval()
    predicted = []
    with torch.no_grad():
        for s in eval_sents:
            enc = tokenizer(
                s.tokens,
                is_split_into_words=True,
                truncation=True,
                max_length=cfg.max_length,
                return_tensors="pt",
            )
            logits = model(**{k: v.to(device) for k, v in enc.items()}).logits[0]
            pred_ids = logits.argmax(-1).tolist()
            word_pred = first_subword_predictions(enc.word_ids(), pred_ids, len(s.tokens))
            predicted.append(bio_to_spans(label_ids_to_bio(word_pred)))
    result = evaluate(eval_sents, predicted)

    n = cfg.eval_limit if cfg.eval_limit is not None else "all"
    run_id = f"E9__conll2003-{cfg.eval_split}-{n}__{cfg.model_name}__ft_e{cfg.epochs}_s{cfg.seed}"
    run_dir = Path(results_dir) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "predictions.jsonl").open("w", encoding="utf-8") as fh:
        for s, spans in zip(eval_sents, predicted, strict=True):
            fh.write(
                json.dumps(
                    {
                        "sentence_id": s.id,
                        "tokens": s.tokens,
                        "gold": [x.model_dump() for x in s.spans],
                        "pred": [x.model_dump() for x in spans],
                        "candidates": [],
                        "parse_ok": True,
                        "retries": 0,
                        "n_unmatched": 0,
                        "n_unknown_type": 0,
                        "raw": "",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    summary = {
        "run_id": run_id,
        "experiment": "E9",
        "dataset": "conll2003",
        "split": cfg.eval_split,
        "limit": cfg.eval_limit,
        "model": cfg.model_name,
        # Prompt-Felder als Platzhalter, damit summary/plots die Zeile verarbeiten
        "use_definition": False,
        "k_examples": 0,
        "use_cot": False,
        "use_candidates": False,
        "output_format": "finetune",
        "max_retries": 0,
        "seed": cfg.seed,
        "prompt_hash": f"ft-e{cfg.epochs}-lr{cfg.lr}-n{cfg.train_limit or 'all'}",
        "f1": result.f1,
        "precision": result.precision,
        "recall": result.recall,
        "per_type_f1": json.dumps({k: round(v.f1, 4) for k, v in result.per_type.items()}),
        "n_sentences": len(eval_sents),
        "parse_fail": 0,
        "retries": 0,
        "unmatched": 0,
        "unknown_type": 0,
        "elapsed_s": round(train_s, 1),
        "n_calls": 0,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "resumed": False,
        "train_sentences": len(train),
        "device": str(device),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info(
        "E9 fertig: F1=%.4f P=%.4f R=%.4f (%d Saetze, Training %.0fs)",
        result.f1,
        result.precision,
        result.recall,
        len(eval_sents),
        train_s,
    )
    return summary
