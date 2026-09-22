"""Konfiguration eines PromptNER-Laufs und Ergebnisstrukturen.

Die vier abschaltbaren Komponenten aus Ashok & Lipton (2023), Tabelle 6:
Definition (``use_definition``), Few-Shot (``k_examples``), Chain-of-Thought
(``use_cot``) und Kandidatenliste (``use_candidates``). ``output_format``
ist eine zusaetzliche Ablation (Paper-Textformat vs. JSON-Schema, Woche 10).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from promptner.domain.entity import Span

OutputFormat = Literal["text", "json"]


class PromptConfig(BaseModel):
    model_config = {"frozen": True}

    dataset: str
    use_definition: bool = True
    k_examples: Literal[0, 2, 5, 10] = 5
    use_cot: bool = True
    use_candidates: bool = True
    output_format: OutputFormat = "text"
    seed: int = 1
    max_retries: int = Field(default=1, ge=0, le=3)
    # Saetze je Aufruf ("Paragraph" im Paper). Gemessen auf 100 CoNLL-Dev-Saetzen, Llama 8B:
    # p1 F1 .820 | p2 .815 | p3 .799 | p5 .722 -> 2 halbiert das KISSKI-Budget fast ohne Verlust.
    paragraph_size: int = Field(default=2, ge=1, le=10)

    def short_name(self) -> str:
        """Eindeutiger Kurzname: **jede** Dimension, nach der aggregiert wird, kommt vor.

        Fehlt eine, teilen sich zwei Konfigurationen einen Lauf-Ordner und die zweite wird
        beim Resume als "bereits vorhanden" uebersprungen (passiert mit ``max_retries`` in E8).
        """
        return (
            f"{self.dataset}_def{int(self.use_definition)}_k{self.k_examples}"
            f"_cot{int(self.use_cot)}_cand{int(self.use_candidates)}"
            f"_{self.output_format}_rt{self.max_retries}_s{self.seed}_p{self.paragraph_size}"
        )


class Candidate(BaseModel):
    """Ein vom LLM genannter Kandidat: Text, Entscheidung, Begruendung, Typname."""

    text: str = Field(..., min_length=1)
    is_entity: bool
    explanation: str = ""
    type_name: str | None = None


class Prediction(BaseModel):
    """Ergebnis fuer einen Satz inkl. Diagnosewerten fuer die Fehleranalyse."""

    sentence_id: str
    spans: list[Span] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)
    raw: str = ""
    parse_ok: bool = True
    retries: int = 0
    n_unmatched: int = 0
    n_unknown_type: int = 0
