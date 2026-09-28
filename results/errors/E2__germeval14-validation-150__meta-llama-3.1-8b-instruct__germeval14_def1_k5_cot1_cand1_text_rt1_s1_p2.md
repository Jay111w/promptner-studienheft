# Fehleranalyse – `E2__germeval14-validation-150__meta-llama-3.1-8b-instruct__germeval14_def1_k5_cot1_cand1_text_rt1_s1_p2`

F1 0.629 · P 0.617 · R 0.641 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 100 |
| Typverwechslung (Grenzen richtig) | 7 |
| Grenzfehler (Typ richtig) | 13 |
| Grenz- und Typfehler | 2 |
| übersehen | 34 |
| erfunden / falsch positiv | 40 |
| Halluzinierte Kandidaten (nicht im Text) | 13 |
| Unbekannte Typnamen | 3 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 45 | 1 | 0 | 1 | 11 |
| ORG | 2 | 22 | 4 | 0 | 7 |
| OTH | 0 | 0 | 14 | 0 | 9 |
| PER | 0 | 0 | 1 | 32 | 7 |
| O | 7 | 6 | 23 | 4 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 41 | 0 | 4 | 2 | 11 |
| ORG | 16 | 6 | 6 | 0 | 7 |
| OTH | 12 | 0 | 2 | 0 | 9 |
| PER | 31 | 1 | 1 | 0 | 7 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `germeval14-validation-0`: Gleich darauf entwirft er seine Selbstdarstellung " [Ecce homo]{OTH} " in enger Auseinandersetzung mit diesem Bild [Jesu]{PER→O} .
- `germeval14-validation-1`: 1980 kam der [Crown]{OTH} als Versuch von [Toyota]{ORG} , sich in der Oberen Mittelklasse zu etablieren , auch nach [Deutschland]{LOC→O} .
- `germeval14-validation-2`: – 4:26 # [Sometime Ago/La Fiesta]{OTH→O} – 23:18 Alle Stücke wurden von [Corea]{PER→O} komponiert mit Ausnahme der einleitenden Improvisation zu [Sometime Ago]{OTH→O} .
- `germeval14-validation-3`: Bis 2013 steigen die Mittel aus dem EU-Budget auf rund 120 Millionen [Euro]{OTH→O} .
- `germeval14-validation-5`: Die [Spinne]{O→OTH} hatte sie mit Seidenfäden an ihrem Schwanz gefesselt und nach oben gezogen .
- `germeval14-validation-6`: In [Deutschland]{LOC} ist nach [StGB]{O→OTH} eine Anwerbung für die [Fremdenlegion]{O→OTH} strafbar .
- `germeval14-validation-8`: Der sechste Lauf der [ADAC GT]{ORG→O} Mastersstand ganz klar im Mittelpunkt des Motorsport-Wochenendes auf dem [Eurospeedway Lausitz]{ORG→LOC} .
- `germeval14-validation-9`: Nach den schwächeren Vorgaben der [Wall Street]{ORG→LOC} vom Vortag setzten die deutschen Standardwerte ihren Konsolidierungskurs fort .
- `germeval14-validation-12`: In der Zeit des [Nationalsozialismus]{O→OTH} war er Wirtschaftsminister und Reichsbankpräsident .
- `germeval14-validation-13`: [Dean Whitehead]{PER} , [Grant Leadbitter]{PER} und [Carlos Edwards]{PER} wurden im Sommer verkauft und [Teemu Tainio]{PER→O} spielt leihweise für [Birmingham]{LOC} .
