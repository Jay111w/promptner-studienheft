# Studienheft-Sample annotieren

Ziel: ~100 Sätze aus einem Studienheft mit Entitäten beschriften. Das ist euer eigener
Datensatz für das Domain-Transfer-Experiment (E2) – und eure sichtbare Eigenleistung.

## Ablauf (ca. 2 Stunden)

1. Vorlage erzeugen: `uv run scripts/annotate_template.py <heft.pdf> --pages 5-12 --out data/studienheft/raw.jsonl`
2. `raw.jsonl` öffnen (VS Code / Antigravity). Eine Zeile = ein Satz:
   ```json
   {"id": "studienheft-0", "tokens": ["Firmengründer", "Wolf", "Peter", "Bree", "arbeitete", "bei", "der", "EU", "."], "spans": [], "source": "studienheft"}
   ```
3. Für jede Entität einen Eintrag in `spans` anlegen. **Token-Indizes, 0-basiert, `end` exklusiv**:
   ```json
   "spans": [{"start": 1, "end": 4, "label": "PER"}, {"start": 7, "end": 8, "label": "ORG"}]
   ```
   → `tokens[1:4]` = `["Wolf", "Peter", "Bree"]`, `tokens[7:8]` = `["EU"]`.
4. Sätze ohne Entität bleiben `"spans": []`. Unbrauchbare Sätze (Tabellenreste, Fußzeilen) einfach löschen.
5. Fertige Datei als `data/studienheft/gold.jsonl` speichern. Prüfen: `uv run python -c "from promptner.data import load_jsonl; print(len(load_jsonl('data/studienheft/gold.jsonl')))"`

## Labels (wie GermEval 2014)

| Label | Was | Beispiele |
|---|---|---|
| `PER` | Personen, auch mit Titel im Namen | „Wolf Peter Bree", „Angela Merkel" (nicht: „die Bundeskanzlerin") |
| `LOC` | Orte, Länder, Regionen, Gebäude mit Eigennamen | „Berlin", „Deutschland", „Alpen" |
| `ORG` | Organisationen, Firmen, Behörden, Institutionen | „EU", „Deutsche Bahn", „Universität Hildesheim" |
| `OTH` | Sonstige Eigennamen: Produkte, Werke, Ereignisse, Gesetze | „Windows 11", „Grundgesetz", „Olympische Spiele 2024" |

## Regeln

- Nur **Eigennamen**, keine Gattungsbegriffe („die Firma", „der Kunde" → nichts).
- Ableitungen sind **keine** Entität („deutsche Unternehmen" → nichts; „Deutschland" → LOC).
- Artikel gehören nicht dazu („die EU" → nur `EU`).
- Bei Zweifel: lieber weglassen und im Bericht als Grenzfall erwähnen.
- Jeder Satz wird von **einer** Person annotiert, 20 Sätze von beiden – daraus berechnen wir die Übereinstimmung (Inter-Annotator-Agreement) für den Bericht.
