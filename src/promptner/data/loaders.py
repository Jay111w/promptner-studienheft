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
