# Fehleranalyse – `E2__germeval14-validation-150__meta-llama-3.1-8b-instruct__germeval14_def1_k5_cot1_cand1_text_rt1_s2_p2`

F1 0.646 · P 0.632 · R 0.660 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 103 |
| Typverwechslung (Grenzen richtig) | 5 |
| Grenzfehler (Typ richtig) | 10 |
| Grenz- und Typfehler | 5 |
| übersehen | 33 |
| erfunden / falsch positiv | 40 |
| Halluzinierte Kandidaten (nicht im Text) | 12 |
| Unbekannte Typnamen | 6 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 42 | 1 | 1 | 2 | 12 |
| ORG | 2 | 26 | 2 | 0 | 5 |
| OTH | 0 | 0 | 13 | 0 | 10 |
| PER | 0 | 0 | 2 | 32 | 6 |
| O | 5 | 10 | 24 | 1 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 40 | 1 | 2 | 3 | 12 |
| ORG | 21 | 4 | 5 | 0 | 5 |
| OTH | 11 | 0 | 2 | 0 | 10 |
| PER | 31 | 0 | 1 | 2 | 6 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `germeval14-validation-0`: Gleich darauf entwirft er seine Selbstdarstellung " [Ecce homo]{OTH} " in enger Auseinandersetzung mit diesem Bild [Jesu]{PER→O} .
- `germeval14-validation-2`: – 4:26 # [Sometime Ago/La Fiesta]{OTH→O} – 23:18 Alle Stücke wurden von [Corea]{PER→O} komponiert mit Ausnahme der einleitenden Improvisation zu [Sometime Ago]{OTH} .
- `germeval14-validation-3`: Bis 2013 steigen die Mittel aus dem EU-Budget auf rund 120 Millionen [Euro]{OTH→O} .
- `germeval14-validation-5`: Die [Spinne]{O→OTH} hatte sie mit Seidenfäden an ihrem Schwanz gefesselt und nach oben gezogen .
- `germeval14-validation-6`: In [Deutschland]{LOC} ist nach [StGB]{O→OTH} eine Anwerbung für die [Fremdenlegion]{O→OTH} strafbar .
- `germeval14-validation-8`: Der sechste Lauf der [ADAC GT]{ORG→O} Mastersstand ganz klar im Mittelpunkt des Motorsport-Wochenendes auf dem [Eurospeedway Lausitz]{ORG→LOC} .
- `germeval14-validation-9`: Nach den schwächeren Vorgaben der [Wall Street]{ORG→LOC} vom Vortag setzten die deutschen Standardwerte ihren Konsolidierungskurs fort .
- `germeval14-validation-10`: [Kolb]{PER} war seit 1986 im [Turnverein]{O→ORG} als Leiter tätig , darunter elf Jahre als Hauptleiter in der Männerriege .
- `germeval14-validation-11`: 1961 wurde auf dem Gelände ein großer [Geflügelzuchtbetrieb]{O→OTH} aufgebaut .
- `germeval14-validation-20`: [B-Säulen]{O→OTH} sucht man vergeblich .
