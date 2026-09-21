"""Laden von Datensaetzen als einheitliche :class:`Sentence`-Listen.

Eigene Daten liegen als JSONL vor (eine Zeile je Satz). HF-Datensaetze folgen
in Task 4.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from promptner.config import get_logger
from promptner.domain import Sentence
from promptner.errors import DataError, ErrorCode

log = get_logger("data.loaders")


def load_jsonl(path: str | Path) -> list[Sentence]:
    p = Path(path)
    if not p.is_file():
        raise DataError(ErrorCode.DATASET_NOT_FOUND, context={"path": str(p)})
    sentences: list[Sentence] = []
    with p.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                sentences.append(Sentence.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValidationError) as exc:
                raise DataError(
                    ErrorCode.DATASET_PARSE_FAILED,
                    context={"path": str(p), "line": n},
                    cause=exc,
                ) from exc
    log.info("JSONL geladen: %s (%d Saetze)", p.name, len(sentences))
    return sentences


def save_jsonl(sentences: list[Sentence], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for s in sentences:
            fh.write(json.dumps(s.model_dump(), ensure_ascii=False) + "\n")
    return p


# --------------------------------------------------------------------------
# Hugging-Face-Datensaetze (Parquet-Konvertierungen, siehe docs/plans/phase-1.md)
# --------------------------------------------------------------------------

from typing import Literal  # noqa: E402

Split = Literal["train", "validation", "test"]
SubtypePolicy = Literal["drop", "merge"]

_CONLL_REPO = "eriktks/conll2003"
_GERMEVAL_REPO = "germeval_14"
_PARQUET_REV = "refs/convert/parquet"


def _hf_split(repo: str, split: str):
    """Laedt einen Split ueber ``datasets`` (monkeypatch-Punkt fuer Tests)."""
    from datasets import load_dataset

    return load_dataset(repo, revision=_PARQUET_REV)[split]


def _germeval_parquet_path(split: str) -> Path:
    """Laedt die Parquet-Datei eines GermEval-Splits (monkeypatch-Punkt fuer Tests)."""
    from huggingface_hub import hf_hub_download

    return Path(
        hf_hub_download(
            _GERMEVAL_REPO,
            f"germeval_14/{split}/0000.parquet",
            repo_type="dataset",
            revision=_PARQUET_REV,
        )
    )


def _rows_to_sentences(
    rows,
    names: list[str],
    *,
    source: str,
    split: str,
    limit: int | None,
    policy: SubtypePolicy | None = None,
) -> list[Sentence]:
    from promptner.data.bio import bio_to_spans

    sentences: list[Sentence] = []
    for i, row in enumerate(rows):
        if limit is not None and i >= limit:
            break
        tags = [_normalise_tag(names[t], policy) for t in row["ner_tags"]]
        tokens = list(row["tokens"])
        if not tokens:
            continue
        sentences.append(
            Sentence(
                id=f"{source}-{split}-{i}", tokens=tokens, spans=bio_to_spans(tags), source=source
            )
        )
    log.info("%s/%s geladen: %d Saetze", source, split, len(sentences))
    return sentences


def _normalise_tag(tag: str, policy: SubtypePolicy | None) -> str:
    """GermEval-Subtypen (``LOCderiv``, ``OTHpart``) auf die vier Haupttypen abbilden."""
    if policy is None or tag == "O":
        return tag
    prefix, label = tag[:2], tag[2:]
    for suffix in ("deriv", "part"):
        if label.endswith(suffix):
            return "O" if policy == "drop" else f"{prefix}{label[: -len(suffix)]}"
    return tag


def load_conll2003(split: Split, limit: int | None = None) -> list[Sentence]:
    """CoNLL-2003 (englisch; PER/ORG/LOC/MISC) aus der HF-Parquet-Konvertierung."""
    try:
        ds = _hf_split(_CONLL_REPO, split)
        names = ds.features["ner_tags"].feature.names
    except Exception as exc:  # noqa: BLE001
        raise DataError(
            ErrorCode.DATASET_NOT_FOUND, context={"dataset": "conll2003", "split": split}, cause=exc
        ) from exc
    return _rows_to_sentences(ds, names, source="conll2003", split=split, limit=limit)


def load_germeval14(
    split: Split, limit: int | None = None, subtype_policy: SubtypePolicy = "drop"
) -> list[Sentence]:
    """GermEval 2014 (deutsch; PER/ORG/LOC/OTH). Subtypen ``*deriv``/``*part`` werden
    standardmaessig verworfen (``drop``) oder auf den Haupttyp abgebildet (``merge``)."""
    import pyarrow.parquet as pq

    try:
        table = pq.read_table(_germeval_parquet_path(split))
        meta = json.loads(table.schema.metadata[b"huggingface"])
        names = meta["info"]["features"]["ner_tags"]["feature"]["names"]
        rows = table.select(["tokens", "ner_tags"]).to_pylist()
    except Exception as exc:  # noqa: BLE001
        raise DataError(
            ErrorCode.DATASET_PARSE_FAILED,
            context={"dataset": "germeval14", "split": split},
            cause=exc,
        ) from exc
    return _rows_to_sentences(
        rows, names, source="germeval14", split=split, limit=limit, policy=subtype_policy
    )


DATASETS: dict[str, tuple[str, ...]] = {
    "conll2003": ("PER", "ORG", "LOC", "MISC"),
    "germeval14": ("PER", "ORG", "LOC", "OTH"),
}


def load_by_name(name: str, split: Split, limit: int | None = None) -> list[Sentence]:
    """Einheitlicher Einstieg fuer den Experiment-Runner."""
    if name == "conll2003":
        return load_conll2003(split, limit=limit)
    if name == "germeval14":
        return load_germeval14(split, limit=limit)
    raise ValueError(f"Unbekannter Datensatz: {name!r}. Bekannt: {sorted(DATASETS)}")
