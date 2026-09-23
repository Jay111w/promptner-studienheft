# promptner-studienheft

Re-Implementierung von **PromptNER** (Ashok & Lipton, 2023) mit offenen Sprachmodellen über den
KISSKI-Endpunkt der GWDG, Ablationen der vier Prompt-Bausteine, Modell- und Sprachvergleich
(CoNLL-2003, GermEval 2014, eigenes Studienheft-Sample) und Fehleranalyse. Projekt im Modul
*Information Extraction in Python* (SoSe 2026), Joshua Amoah und Alireza Vahidinia.

Kein Training, keine GPU: Das Modell bekommt Typdefinitionen, wenige Beispiele mit Begründung
und listet Kandidaten mit einer Ja/Nein-Entscheidung je Kandidat. Die Antwort wird geparst,
auf Token-Spans abgebildet und mit seqeval (Entity-Level-F1) bewertet.

## Schnellstart

```bash
uv sync --extra demo                    # Python ≥ 3.11; --extra demo nur für die PySide6-Oberfläche
cp .env.example .env                    # KISSKI_API_KEY=... eintragen (nie committen)
uv run pytest -m "not live and not network"   # 220+ Tests, ohne Netz und ohne Key
uv run promptner models                 # prüft Key und listet die Modell-IDs
uv run scripts/run_smoke.py --limit 20  # erster echter Lauf: 20 CoNLL-Dev-Sätze, F1 in ~10 s
```

Ohne Key laufen alle Unit-Tests (Fake-LLM). Mit Key kostet jeder Aufruf Budget – siehe unten.

### Ergebnisse ohne Key nachspielen

Alle Antworten des Endpunkts liegen als Kopie im Repository (`replay-cache/`, rund 1 MB). Damit
lässt sich jedes Experiment **ohne API-Key, ohne Kosten und mit identischen Zahlen** neu
rechnen – der Lauf holt jede Antwort aus dem Cache, statt zu fragen:

```bash
CACHE_DIR=replay-cache RESULTS_DIR=nachgespielt uv run promptner run --experiment E4 --seeds 1
# -> F1=0.8153 (volle Konfiguration) und F1=0.8214 (ohne Definition), in ~3 Sekunden
```

Das ist der empfohlene Weg, die Ergebnisse dieser Arbeit zu prüfen: Parser, Alignment, Metrik
und Aggregation laufen vollständig durch, nur der Netzaufruf entfällt. Geprüft mit einem
frischen Klon ohne `.env`. Die Kopie entsteht mit `uv run scripts/export_cache.py` (SQLite-
Backup-API, funktioniert auch während ein Experiment schreibt).

## Experimente reproduzieren

Jedes Experiment ist ein benannter Satz von Läufen (Datensatz × Prompt-Konfiguration × Modell ×
Seed). Ein Lauf schreibt `results/runs/<run_id>/predictions.jsonl` und `summary.json`; gleiche
Prompts werden aus dem Antwort-Cache (`.cache/llm`) bedient, abgebrochene Läufe setzen fort.

| Experiment | Frage | Variable |
|---|---|---|
| E1 | Headline auf den Test-Sets | CoNLL-Test, GermEval-Test (nur einmal ausführen) |
| E2 | Sprache / Domäne | CoNLL vs. GermEval vs. Studienheft |
| E3 | Modell-Tausch | `--models a,b,c` |
| E4 | Ablation Definition | `use_definition` |
| E5 | Ablation Chain-of-Thought | `use_cot` |
| E6 | Ablation Few-Shot | k ∈ {0, 2, 5, 10} |
| E7 | Ablation Kandidatenliste | `use_candidates` |
| E8 | Ausgabeformat + Retry | Text (Paper) vs. JSON-Schema, Retry an/aus |
| E9 | Klassische Baseline | `scripts/train_bert.py` (BERT + Linear-Kopf, lokal; `--dataset germeval14 --model bert-base-german-cased` für die deutsche Referenz) |
| E10 | Sätze je Aufruf | `paragraph_size` ∈ {1, 2, 3, 5} |

```bash
uv run promptner run --experiment E4 --dry-run          # nur auflisten
uv run promptner run --experiment E4                    # Standard: 150 Sätze, Seeds 1,2, 2 Sätze je Aufruf
uv run promptner run --experiment E3 --models qwen3.8-27b,mistral-medium-3.5-128b,qwen3.5-397b-a17b --seeds 1
uv run promptner summary                                # results/summary.csv, Mittelwert ± Std über Seeds
uv run promptner plots                                  # results/plots/E*.png
uv run promptner errors --run <run_id>                  # results/errors/<run_id>.md: Matrix, Grenzfehler, Beispiele
```

Mehrere Experimente nacheinander, gedrosselt, mit Neustart bei Abbruch (Mac bleibt wach):

```bash
scripts/night.sh E4 E5 E7                # Log unter logs/night-*.log
SEEDS=3 LIMIT=300 scripts/night.sh E6    # Umgebungsvariablen überschreiben die Defaults
```

### Budget

Der KISSKI-Key erlaubt je Key **30 Aufrufe/min, 200/h, 1000/Tag, 3000/Monat**. Der Client
drosselt sich selbst (`LLM_CALLS_PER_MINUTE`, `LLM_CALLS_PER_HOUR` in `.env`) und wartet bei
429 so lange, wie der Endpunkt vorgibt. Deshalb die Defaults 150 Sätze je Lauf und zwei Sätze je
Aufruf (`paragraph_size=2`, gemessen: −0.5 F1 gegenüber Einzelsätzen bei halben Kosten; fünf
Sätze kosten −10). Ein Lauf ≈ 75 Aufrufe.

## Eigenes Sample (Studienheft)

Das Studienheft-PDF selbst wird **nicht** versioniert (`*.pdf` in `.gitignore`) – nur die
daraus erzeugte, annotierte JSONL. Die Abbildungen unter `results/figures/` sind davon
ausgenommen.

```bash
uv run scripts/annotate_template.py heft.pdf --pages 5-12 --out data/studienheft/raw.jsonl
# annotieren nach data/studienheft/ANNOTATION.md -> data/studienheft/gold.jsonl
uv run promptner agreement --a gold_a.jsonl --b gold_b.jsonl   # Uebereinstimmung der 20 gemeinsamen Saetze
uv run promptner run --experiment E2 --datasets studienheft
```

## Aufbau

```
src/promptner/
  prompting/   definitions.py (Typdefinitionen EN/DE) · examples.py (Few-Shot-Pool, Auswahl per Seed)
               builder.py (Prompt nach Figure 1; Beispiele als Chat-Turns)
  llm/         client.py (OpenAI-SDK gegen KISSKI, Drossel, retry-after) · parser.py (Antwort -> Kandidaten -> Spans)
               cache.py (Antwort-Cache)
  pipeline/    predict.py (Absatz -> Prompt -> LLM -> Spans je Satz, Format-Retry)
  data/        loaders.py (CoNLL-2003, GermEval 2014, JSONL) · bio.py · segment.py
  eval/        metrics.py (seqeval) · error_analysis.py · plots.py
  experiments/ spec.py (E1-E8) · runner.py (Läufe, Resume) · aggregate.py
  cli.py       promptner run | summary | plots | errors | agreement | models
src/korrektor/ Studienheft-Korrektor (PDF-Extraktion, PySide6-Oberfläche) - Anwendungs-Demo
docs/          LOGBUCH.md (Befunde und Entscheidungen mit Zahlen) · plans/ · bericht/GLIEDERUNG.md
results/       runs/ · summary.csv · plots/ · errors/
```

Abweichungen vom Paper und ihre Begründung stehen in `docs/LOGBUCH.md` (Chat-Turns für die
Beispiele, offene Modelle, Absatzgröße). Regeln für Mitarbeit und Agenten: `AGENTS.md`.

## Lizenz

MIT.
