"""Antwort-Cache auf Platte: jede (Modell, Prompt, Seed)-Kombination wird nur einmal angefragt.

Macht Wiederholungen kostenlos und deterministisch; Schluessel ist ein SHA-256
ueber Modell-ID, System- und User-Prompt sowie Seed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import diskcache

from promptner.llm.client import ChatRequest


def cache_key(model: str, request: ChatRequest, seed: int | None) -> str:
    h = hashlib.sha256()
    for part in (
        model,
        request.system,
        request.user,
        str(seed),
        request.json_mode and "json" or "text",
    ):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


class ResponseCache:
    def __init__(self, directory: str | Path) -> None:
        self._cache = diskcache.Cache(str(directory))

    def get(self, key: str) -> str | None:
        value = self._cache.get(key)
        return value if isinstance(value, str) else None

    def put(self, key: str, value: str) -> None:
        self._cache.set(key, value)

    def close(self) -> None:
        self._cache.close()
