# Regeln für alle Agenten in diesem Repo (Claude Code, Gemini/Antigravity, Menschen)

Dieses Repo ist eine Seminarabgabe (*Information Extraction in Python*, Abgabe 30.09.2026).
Bewertet wird **Verständnis der Methode + Qualität der Experimente**, nicht Codemenge.
Übergeordneter Plan: `../CODING_PLAN.md`. Detailpläne je Phase liegen lokal unter
`docs/plans/phase-N.md` und sind nicht Teil des Repos.

## Was hier gebaut wird

- `src/promptner/` — wissenschaftlicher Kern: Re-Implementierung von **PromptNER** (Ashok & Lipton 2023),
  Datensätze (CoNLL-2003, GermEval 2014, Studienheft-Sample), seqeval-Evaluation, Experiment-Runner, Ablationen.
- `src/korrektor/` — bestehende Demo-Anwendung (PDF-Korrektorat, PySide6). **Nicht umbauen**, nur den
  Demo-Modus „Entitäten extrahieren" ergänzen (Phase 7). Muss weiter 79 Tests grün haben.

## Werkzeuge — keine Ausnahmen

| Zweck | Befehl |
|---|---|
| Umgebung | `uv sync --extra demo` (nie `pip install`) |
| Tests | `QT_QPA_PLATFORM=offscreen uv run pytest` — muss vor **jedem** Commit grün sein |
| Lint + Format | `uv run ruff check src tests scripts && uv run ruff format src tests scripts` |
| Skript ausführen | `uv run scripts/<name>.py` |
| Neue Abhängigkeit | nur, wenn sie in `CODING_PLAN.md` Abschnitt 6 steht; sonst erst im Plan eintragen |

## Arbeitsweise

1. **Test zuerst.** Für jede neue Funktion existiert ein Test in `tests/promptner/`, der vor der Implementierung rot ist.
2. **Kein echter LLM in Tests.** LLM-Aufrufe laufen über `promptner.llm.client.LlmClient`; Tests injizieren ein
   Fake-SDK (siehe `tests/promptner/unit/test_llm_client.py`). Tests, die einen echten Key brauchen, tragen
   `@pytest.mark.live` und werden in CI übersprungen.
3. **Kein `pytest.skip`, kein `# noqa` ohne Begründung im Kommentar, keine gelöschten Tests.**
4. **Ein Task = ein Commit.** Commit-Message: erste Zeile imperativ (`feat(data): CoNLL-2003-Loader`), darunter die
   letzte Zeile der `pytest`-Ausgabe (z. B. `112 passed in 4.1s`) als Beleg.
5. **Fehler werden in `PromptNerError` übersetzt** (`src/promptner/errors.py`) mit passendem `ErrorCode`.
   Keine nackten `Exception`-Weitergaben aus Bibliotheken.
6. **Pfade und Signaturen aus dem Phasenplan sind verbindlich.** Andere Namen oder Modulorte nur nach Rücksprache —
   ein anderer Agent baut parallel gegen dieselben Schnittstellen.
7. **Umlaute in Strings, die Menschen lesen** (Prompts auf Deutsch, Fehlermeldungen, Bericht). ASCII nur in Bezeichnern.
8. **Kein Key im Code, in Logs oder in Commits.** `.env` ist ausgeschlossen; `SecretStr` bleibt.
9. **Ergebnisse sind Daten, keine Behauptungen.** Jeder Experimentlauf schreibt eine CSV nach `results/` mit
   Modell-ID, Prompt-Hash, Seed, Datensatz, Konfiguration. „Fertig" heißt: Datei liegt vor, Zahlen stehen drin.

## Für Gemini / Antigravity im Besonderen

- Du bekommst Aufträge der Form „Tasks 3–5 aus `docs/plans/phase-N.md`" (lokal). Baue genau diese, nicht mehr.
- Ändere keine Architektur „zur Vereinfachung". Wenn etwas im Plan nicht umsetzbar ist, schreibe es in
  `docs/plans/OPEN_QUESTIONS.md` und mache mit dem nächsten Task weiter.
- Wenn ein Test nicht grün wird: nicht den Test ändern, sondern in `OPEN_QUESTIONS.md` dokumentieren.

## Domäne in zwei Sätzen

NER = Named Entity Recognition: Spans im Satz als PER/LOC/ORG/MISC (CoNLL) bzw. PER/LOC/ORG/OTH (GermEval) markieren.
PromptNER = das LLM bekommt Typ-Definitionen + k Beispiele mit Begründung, listet Kandidaten und entscheidet je Kandidat;
wir messen Span-Level-F1 (seqeval, strict, IOB2) und variieren Definitionen / Begründungen / k / Modell / Datensatz.

## Dokumentation, die mitlaufen muss

- `docs/LOGBUCH.md`: Jeder Befund aus echten Läufen (Zahlen!) und jede Entscheidung mit Begründung
  bekommt einen datierten Eintrag. Das ist das Rohmaterial für den Bericht.
- `../CODING_PLAN.md` §0: Status-Tabelle und „nächste Befehle" nach jeder Phase aktualisieren.
