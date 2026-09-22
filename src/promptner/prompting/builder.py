"""Baut den PromptNER-Prompt nach Figure 1 von Ashok & Lipton (2023).

Aufbau: ``Defn:`` (optional) -> ``Q:`` -> k Beispiele (``Paragraph:`` + ``Answer:``
mit Kandidatenzeilen) -> Zielsatz mit leerem ``Answer:``. Jede Komponente laesst
sich per :class:`PromptConfig` abschalten; ``output_format="json"`` ersetzt die
Zeilen durch ein JSON-Objekt (Zusatz-Ablation, Woche 10).
"""

from __future__ import annotations

import hashlib
import json

from promptner.domain import Candidate, PromptConfig, Sentence
from promptner.llm.client import ChatRequest
from promptner.prompting.definitions import DEFINITIONS, QUESTION
from promptner.prompting.examples import select_examples

_WORDS = {
    "en": {
        "paragraph": "Paragraph",
        "answer": "Answer",
        "true": "True",
        "false": "False",
        "q_entities_only": (
            "Given the paragraph below, identify the entities it contains and for each "
            "entry explain why it is an entity:"
        ),
        "q_no_cot": (
            "Given the paragraph below, identify a list of possible entities and state for "
            "each entry whether it is an entity:"
        ),
        "q_no_cot_entities_only": "Given the paragraph below, identify the entities it contains:",
        "none": "None",
        "system": (
            "You are a careful named-entity annotator. Follow the answer format of the examples "
            "exactly: one numbered line per candidate. Quote candidate text exactly as it appears "
            "in the paragraph. Do not add commentary before or after the list."
        ),
        "json_instruction": (
            'Answer with a single JSON object of the form {"candidates": [{"text": "...", '
            '"is_entity": true, "explanation": "...", "type_name": "..."}]} and nothing else.'
        ),
    },
    "de": {
        "paragraph": "Absatz",
        "answer": "Antwort",
        "true": "True",
        "false": "False",
        "q_entities_only": (
            "Nenne für den folgenden Absatz die enthaltenen Entitäten und begründe für jeden "
            "Eintrag, warum er eine Entität ist:"
        ),
        "q_no_cot": (
            "Nenne für den folgenden Absatz eine Liste möglicher Entitäten und gib für jeden "
            "Eintrag an, ob er eine Entität ist:"
        ),
        "q_no_cot_entities_only": "Nenne für den folgenden Absatz die enthaltenen Entitäten:",
        "none": "Keine",
        "system": (
            "Du bist ein sorgfältiger Annotator für Eigennamen. Halte dich exakt an das "
            "Antwortformat der Beispiele: eine nummerierte Zeile je Kandidat. Zitiere den "
            "Kandidatentext genau so, wie er im Absatz steht. Keine Kommentare vor oder nach der Liste."
        ),
        "json_instruction": (
            'Antworte mit genau einem JSON-Objekt der Form {"candidates": [{"text": "...", '
            '"is_entity": true, "explanation": "...", "type_name": "..."}]} und sonst nichts.'
        ),
    },
}
LANGUAGE: dict[str, str] = {"conll2003": "en", "germeval14": "de", "studienheft": "de"}


def _w(config: PromptConfig) -> dict[str, str]:
    return _WORDS[LANGUAGE[config.dataset]]


def format_answer(candidates: list[Candidate], config: PromptConfig) -> str:
    """Kandidatenliste im Antwortformat des Papers (oder als JSON)."""
    w = _w(config)
    shown = [c for c in candidates if c.is_entity or config.use_candidates]
    if config.output_format == "json":
        payload = [
            {
                "text": c.text,
                "is_entity": c.is_entity,
                **({"explanation": c.explanation} if config.use_cot else {}),
                **({"type_name": c.type_name} if c.is_entity else {}),
            }
            for c in shown
        ]
        return json.dumps({"candidates": payload}, ensure_ascii=False)
    if not shown:
        return w["none"]
    lines = []
    for i, c in enumerate(shown, start=1):
        flag = w["true"] if c.is_entity else w["false"]
        typ = f" ({c.type_name})" if c.is_entity and c.type_name else ""
        if config.use_cot:
            lines.append(f"{i}. {c.text} | {flag} | {c.explanation}{typ}")
        else:
            lines.append(f"{i}. {c.text} | {flag}{typ}")
    return "\n".join(lines)


def _question(config: PromptConfig) -> str:
    w = _w(config)
    if config.use_cot and config.use_candidates:
        return QUESTION[config.dataset]
    if config.use_cot:
        return w["q_entities_only"]
    if config.use_candidates:
        return w["q_no_cot"]
    return w["q_no_cot_entities_only"]


def build_prompt(config: PromptConfig, sentence: Sentence) -> ChatRequest:
    w = _w(config)
    parts: list[str] = []
    if config.use_definition:
        parts.append(f"Defn: {DEFINITIONS[config.dataset]}")
    question = _question(config)
    if config.output_format == "json":
        question = f"{question}\n{w['json_instruction']}"
    parts.append(f"Q: {question}")
    preamble = "\n\n".join(parts)

    def ask(text: str) -> str:
        return f"{w['paragraph']}: {text}\n\n{w['answer']}:"

    # Figure 1 als Chat: Defn + Q stehen vor dem ersten Absatz, jedes Beispiel ist ein
    # eigener User/Assistant-Turn, der Zielsatz die letzte User-Nachricht.
    turns: list[tuple[str, str]] = []
    for ex in select_examples(config.dataset, config.k_examples, config.seed):
        asked = ask(" ".join(ex.tokens))
        if not turns:
            asked = f"{preamble}\n\n{asked}"
        turns.append((asked, format_answer(list(ex.candidates), config)))
    user = ask(sentence.text) if turns else f"{preamble}\n\n{ask(sentence.text)}"
    return ChatRequest(
        system=w["system"],
        user=user,
        json_mode=config.output_format == "json",
        turns=tuple(turns),
    )


def prompt_hash(config: PromptConfig) -> str:
    """Kurzer, stabiler Hash ueber alles, was den Prompt bestimmt (fuer Ergebnisdateien)."""
    probe = Sentence(id="probe", tokens=["x"])
    req = build_prompt(config, probe)
    digest = hashlib.sha256(req.full_text.encode("utf-8")).hexdigest()
    return digest[:12]
