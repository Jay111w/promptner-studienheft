# promptner-studienheft

Re-Implementierung von **PromptNER** (Ashok & Lipton, 2023) mit offenen Sprachmodellen über den
KISSKI-Endpunkt der GWDG, mit Ablationen der vier Prompt-Bausteine, einem Modell- und
Sprachvergleich über CoNLL-2003, GermEval 2014 und ein selbst annotiertes Studienheft-Sample sowie
einer Fehleranalyse.

Dies ist der Coding-Teil der Prüfungsleistung im Modul *Information Extraction in Python*
(Sommersemester 2026) von Joshua Amoah und Alireza Vahidinia. Der schriftliche Bericht wird separat
abgegeben und erklärt Methode und Ergebnisse, während dieses Repository sie reproduzierbar macht.

## Was das Verfahren tut

Kein Training und keine GPU. Das Modell bekommt im Prompt Typdefinitionen, wenige gelöste Beispiele
mit Begründung und die Aufgabe, im Zieltext Kandidaten aufzulisten und jeden davon anzunehmen oder
zu verwerfen. Die Antwort wird geparst, auf Token-Spans abgebildet und mit seqeval als
Entity-Level-F1 bewertet.

## Schnellstart

```bash
uv sync --extra demo                           # Python >= 3.11, --extra demo nur fuer die PySide6-Oberflaeche
uv run pytest -m "not live and not network"    # 243 Tests, ohne Netz und ohne Key
```

Für eigene Läufe gegen den Endpunkt zusätzlich:

```bash
cp .env.example .env                           # KISSKI_API_KEY=... eintragen, nie committen
uv run promptner models                        # prueft den Key und listet die Modell-IDs
uv run scripts/run_smoke.py --limit 20         # erster echter Lauf, 20 CoNLL-Saetze, F1 in ~10 s
```

## Ergebnisse prüfen, ohne API-Key

Alle Antworten des Endpunkts liegen als Kopie im Repository unter `replay-cache/`. Damit lässt sich
jedes Experiment ohne Zugangsschlüssel, ohne Kosten und mit identischen Zahlen neu rechnen, weil der
Lauf jede Antwort aus dieser Kopie holt, statt das Modell zu fragen.

```bash
CACHE_DIR=replay-cache RESULTS_DIR=nachgespielt uv run promptner run --experiment E4 --seeds 1
# -> F1=0.8153 (volle Konfiguration) und F1=0.8214 (ohne Definition), in etwa 3 Sekunden
```

Das ist der empfohlene Weg zum Nachvollziehen. Parser, Alignment, Metrik und Aggregation laufen
vollständig durch, nur der Netzaufruf entfällt. Geprüft in einem frischen Klon ohne `.env`.

## Die Experimente

Ein Experiment ist ein benannter Satz von Läufen aus Datensatz, Prompt-Konfiguration, Modell und
Seed. Jeder Lauf schreibt `results/runs/<run_id>/` mit `predictions.jsonl` und `summary.json`.
Abgebrochene Läufe setzen fort, und gleiche Prompts werden aus dem Antwort-Cache bedient.

| Experiment | Frage | Variable |
|---|---|---|
| E1 | Leistung auf den Test-Splits | CoNLL-Test, GermEval-Test, nur einmal ausführen |
| E2 | Sprache und Domäne | CoNLL gegen GermEval gegen Studienheft |
| E3 | Modellgröße | `--models a,b,c` |
| E4 | Ablation Typdefinitionen | `use_definition` |
| E5 | Ablation Begründung | `use_cot` |
| E6 | Ablation Few-Shot | k aus 0, 2, 5, 10 |
| E7 | Ablation Kandidatenliste | `use_candidates` |
| E8 | Ausgabeformat und Retry | Text gegen JSON-Schema, Retry an und aus |
| E9 | Trainierte Baseline | `scripts/train_bert.py`, BERT mit Linear-Kopf, lokal |
| E10 | Sätze je Aufruf | `paragraph_size` aus 1, 2, 3, 5 |

```bash
uv run promptner run --experiment E4 --dry-run   # nur auflisten, nichts ausfuehren
uv run promptner run --experiment E4             # Standard: 150 Saetze, Seeds 1 und 2
uv run promptner summary                         # results/summary.csv, Mittelwert und Std ueber Seeds
uv run promptner plots                           # results/plots/E*.png
uv run promptner errors --run <run_id>           # Verwechslungsmatrix, Grenzfehler, Beispielsaetze
```

Mehrere Experimente nacheinander, gedrosselt und mit Neustart nach Abbruch:

```bash
scripts/night.sh E4 E5 E7                        # Log unter logs/night-*.log
SEEDS=3 LIMIT=300 scripts/night.sh E6            # Umgebungsvariablen ueberschreiben die Defaults
```

Der Endpunkt erlaubt je Schlüssel 30 Aufrufe pro Minute, 200 pro Stunde, 1 000 pro Tag und 3 000 pro
Monat. Der Client drosselt sich selbst und wartet bei einer Überschreitung so lange, wie der
Endpunkt vorgibt. Daher die Voreinstellungen von 150 Sätzen je Lauf und zwei Sätzen je Aufruf, was
etwa 75 Aufrufe je Lauf ergibt.

## Eigenes Sample

Die 152 annotierten Sätze stammen aus einem Fernstudienbrief zur Verwaltungsdigitalisierung. Das
PDF selbst wird nicht versioniert, nur die daraus erzeugte JSONL. Beide Autoren haben je 66 Sätze
allein und 20 Sätze gemeinsam annotiert, woraus sich die Übereinstimmung messen lässt.

```bash
uv run scripts/annotate_template.py heft.pdf --pages 5-12 --out data/studienheft/raw.jsonl
uv run scripts/preannotate.py --inp data/studienheft/raw.jsonl --out data/studienheft/vorschlag.jsonl
uv run scripts/split_annotation.py --vorschlag data/studienheft/vorschlag.jsonl
# beschriften in tools/annotations-oberflaeche/, Ausgabe je Person als JSON
uv run scripts/import_annotation.py --datei annotation_joshua.json
uv run promptner agreement --a data/studienheft/gold_gemeinsam_joshua.jsonl \
                           --b data/studienheft/gold_gemeinsam_alireza.jsonl
uv run scripts/build_gold.py                     # -> data/studienheft/gold.jsonl
uv run promptner run --experiment E2 --datasets studienheft
```

`build_gold.py` setzt die vorab festgelegten Annotationsrichtlinien maschinell durch. Die Regeln
stehen in `src/promptner/data/normalize.py`, das Protokoll in
`results/richtlinien-normalisierung.md`, und beide Übereinstimmungszahlen liegen unter
`results/annotator-agreement*.md`.

## Aufbau

```
src/promptner/
  prompting/   definitions.py (Typdefinitionen EN/DE) - examples.py (Few-Shot-Pool, Auswahl per Seed)
               builder.py (Prompt-Aufbau, Beispiele als Chat-Turns)
  llm/         client.py (OpenAI-SDK gegen KISSKI, Drossel) - parser.py (Antwort zu Kandidaten zu Spans)
               cache.py (Antwort-Cache)
  pipeline/    predict.py (Absatz zu Prompt zu Modell zu Spans, Format-Retry)
  data/        loaders.py (CoNLL-2003, GermEval 2014, JSONL) - bio.py - segment.py - normalize.py
  eval/        metrics.py (seqeval) - error_analysis.py - plots.py
  experiments/ spec.py (E1 bis E10) - runner.py (Laeufe, Resume) - aggregate.py
  cli.py       promptner run | summary | plots | errors | agreement | models
src/korrektor/ Studienheft-Korrektor mit PDF-Extraktion und PySide6-Oberflaeche, Anwendungs-Demo
tools/         annotations-oberflaeche/, Klick-Oberflaeche fuer die Annotation
results/       runs/ - summary.csv - plots/ - errors/ - figures/
```

Alle Ergebnisse stehen aggregiert in `results/summary.csv`, die Fehleranalysen je Lauf unter
`results/errors/`. Eingeordnet und diskutiert werden sie im schriftlichen Bericht.

## Lizenz

MIT.
