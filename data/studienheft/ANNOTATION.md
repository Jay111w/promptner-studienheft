# Studienheft-Sample annotieren

Ziel: ~100 Sätze aus einem Studienheft mit Entitäten beschriften. Das ist euer eigener
Datensatz für das Domain-Transfer-Experiment (E2) – und eure sichtbare Eigenleistung.

## Die Quelle

Wir annotieren den Studienbrief **„Grundlagen des E-Governments und des Informationsmanagements"**
aus dem MBA-Fernstudienprogramm der Hochschule Koblenz (zfh), als öffentliche Leseprobe abrufbar
unter <https://www.hs-koblenz.de/wiso/mba-fernstudienprogramm/fuer-studieninteressierte/leseproben-studienbriefe>.
Das PDF liegt als `data/studienheft/quelle.pdf` im Arbeitsverzeichnis und wird nicht versioniert.

Warum dieser Text und nicht das ILS-Heft zu Webvideos, das uns ebenfalls vorlag: In 1 005 Sätzen
jenes Hefts tragen nur 53 einen Eigennamen, also 5 %. Hier sind es rund ein Drittel. Für eine
Messung mit 100 Sätzen ist das der Unterschied zwischen etwa 20 und etwa 50 Entitäten.

**Gewählter Bereich:** Seiten 27 bis 40, das sind die Kapitel zu den rechtlichen Grundlagen.
Die Vorlage enthält 152 Sätze, ihr braucht davon etwa 100 brauchbare.

## Ablauf (ca. 2 Stunden)

1. Vorlage erzeugen (schon geschehen, der Befehl steht hier zum Nachvollziehen):
   `uv run scripts/annotate_template.py data/studienheft/quelle.pdf --pages 27-40 --out data/studienheft/raw.jsonl`
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

## Diese Quelle im Besonderen

Der Text handelt von Verwaltungsdigitalisierung, deshalb sieht die Typverteilung anders aus als
in den Nachrichtentexten von CoNLL und GermEval. Häufig sind Gesetze und Programme, also `OTH`,
gefolgt von Behörden und Institutionen als `ORG`. Orte kommen fast nur als Staaten und
Bundesländer vor, Personen so gut wie nie. Diese Schieflage ist kein Fehler der Auswahl, sondern
ein Merkmal der Domäne, und sie gehört genau so in den Bericht.

Drei Entscheidungen, die wir vorab festlegen, damit beide gleich annotieren:

| Fall | Typ | Begründung |
|---|---|---|
| `Deutschland`, `Rheinland-Pfalz`, `Schleswig-Holstein` | `LOC` | Staaten und Bundesländer immer als Ort, auch wenn sie im Satz handeln („Rheinland-Pfalz definiert hierin …“) |
| `Europäische Union`, `Bundesministerium des Innern`, `KGSt` | `ORG` | benannte Institutionen und Behörden |
| `Onlinezugangsgesetz`, `OZG`, `EGovGRP`, `DSGVO`, `eEurope2002` | `OTH` | Gesetze, Verordnungen und benannte Programme |

Abkürzungen werden wie der ausgeschriebene Name behandelt, also ist `OZG` ein eigener Span vom
Typ `OTH`. Gattungsbegriffe bleiben unmarkiert, `die Behörde`, `das Gesetz` und `der Bund` sind
also keine Entitäten, `der Bundesrat` dagegen schon.

## Regeln

- Nur **Eigennamen**, keine Gattungsbegriffe („die Firma", „der Kunde" → nichts).
- Ableitungen sind **keine** Entität („deutsche Unternehmen" → nichts; „Deutschland" → LOC).
- Artikel gehören nicht dazu („die EU" → nur `EU`).
- Bei Zweifel: lieber weglassen und im Bericht als Grenzfall erwähnen.
- Jeder Satz wird von **einer** Person annotiert, 20 Sätze von beiden – daraus berechnen wir die Übereinstimmung (Inter-Annotator-Agreement) für den Bericht.

## Übereinstimmung prüfen (die 20 gemeinsamen Sätze)

Beide legen ihre Fassung getrennt ab, dann:

```
uv run promptner agreement --a data/studienheft/gold_alireza.jsonl \
                           --b data/studienheft/gold_joshua.jsonl
```

Das Werkzeug vergleicht nur Sätze, deren `id` in beiden Dateien vorkommt, und bricht ab, wenn
die Tokens derselben `id` voneinander abweichen (dann wurde nicht dieselbe Vorlage annotiert).
Es meldet:

- **Span-F1** – exakte Grenzen *und* Typ, dieselbe Metrik wie bei den Modellläufen. Diese Zahl
  kommt in den Bericht, weil sie direkt neben den Modellzahlen lesbar ist.
- **Cohen's Kappa** je Token über die BIO-Tags – die in der Literatur übliche Zahl. Sie fällt
  bei NER optimistisch aus, weil die meisten Tokens `O` sind; deshalb steht sie nur daneben.
- **Uneinige Sätze** mit beiden Lesarten – das ist die Liste, die ihr gemeinsam durchgeht.
  Danach entscheidet ihr je Fall und schreibt die Einigung in `gold.jsonl`.

Ein Span-F1 unter etwa 0,80 heißt meist nicht, dass jemand geschludert hat, sondern dass die
Richtlinien oben eine Lücke haben – dann Regel ergänzen und die betroffenen Sätze nachziehen.
Der Bericht in `docs/annotator-agreement.md` wird bei jedem Lauf neu geschrieben.
