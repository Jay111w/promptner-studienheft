# Fehleranalyse – `E2__studienheft-validation-150__meta-llama-3.1-8b-instruct__studienheft_def1_k5_cot1_cand1_text_rt1_s2_p2`

F1 0.560 · P 0.439 · R 0.772 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 61 |
| Typverwechslung (Grenzen richtig) | 2 |
| Grenzfehler (Typ richtig) | 8 |
| Grenz- und Typfehler | 0 |
| übersehen | 8 |
| erfunden / falsch positiv | 68 |
| Halluzinierte Kandidaten (nicht im Text) | 14 |
| Unbekannte Typnamen | 4 |
| Format-Fehler (parse_ok=false) | 2 |
| Retries | 2 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 11 | 0 | 0 | 0 | 2 |
| ORG | 0 | 8 | 0 | 0 | 3 |
| OTH | 0 | 0 | 48 | 0 | 3 |
| PER | 0 | 0 | 2 | 2 | 0 |
| O | 11 | 11 | 46 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 11 | 0 | 0 | 0 | 2 |
| ORG | 7 | 0 | 1 | 0 | 3 |
| OTH | 41 | 0 | 7 | 0 | 3 |
| PER | 2 | 2 | 0 | 0 | 0 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `studienheft-2`: Rechtliche Grundlagen Da die Behörden in [Deutschland]{LOC} als Teil der Exekutive öffentlich-rechtliche Aufgaben des Staates wahrnehmen , unterliegt auch das [E-Government]{O→OTH} einigen rechtlichen Rahmenbedingungen .
- `studienheft-6`: So wäre hier beispielsweise der diesbezüglich erste Aktionsplan mit dem Namen „ [eEurope2002]{OTH} “ zu nennen , mit dem das Ziel verfolgt wurde , die Verbreitung des Zugangs zum Internet in [Europa]{LOC→O} zu forcieren , die Kommunikationsnetze für den Wettbewerb zu öffnen und somit auch die Internetnutzung zu fördern .
- `studienheft-11`: In diesem Zusammenhang ist auch darauf hinzuweisen , dass die [Europäische Union]{ORG→O} mittlerweile die „ [Digitale Dekade 2030]{OTH} “ verkündet hat .
- `studienheft-12`: Europäische Aktionspläne [Die Erklärung zu digitalen Rechten und Grundsätzen]{O→OTH} wurde dabei von der Europäischen Kommission , dem [Parlament]{O→ORG} sowie dem [Rat]{O→ORG} unterzeichnet .
- `studienheft-14`: Auf der obersten Ebene wurden hier folgende Handlungsfelder benannt :  Menschen und ihre Rechte in den Mittelpunkt des digitalen Wandels rücken  Unterstützung von Solidarität und Inklusion  Gewährleistung der Wahlfreiheit im Internet  Förderung der Beteiligung am digitalen öffentlichen Raum  Erhöhung der Sicherheit , des Schutzes und der Befähigung des Einzelnen  Förderung der Nachhaltigkeit der digitalen Zukunft Hieraus wurden auch legislative Regelungserfordernisse in Bezug auf die nachfolgend aufgeführten Aspekte abgeleitet :  [Künstliche Intelligenz]{O→OTH}  [Umgang mit Daten]{O→OTH}  Onlineplattformen  [Informationssicherheit]{O→OTH}  [Presse - / Medienfreiheit]{O→OTH} Als Konsequenz der zuvor aufgeführten Aktionspläne der [EU-Kommission]{ORG} wären beispielsweise auch folgende Verordnungen zu nennen :  [Gesetz über künstliche Intelligenz]{OTH→OTH pred=„Gesetz über künstliche Intelligenz ( Verordnung ( EU ) 2024 / 1689 )“} ( Verordnung ( EU ) 2024 / 1689 )  Europäische digitale Identität ( Verordnung ( EU ) Nr .
- `studienheft-15`: 910 / 2014 )  [Datenschutz-Grundverordnung]{OTH→OTH pred=„Datenschutz-Grundverordnung ( Verordnung ( EU ) 2016 / 679 )“} ( Verordnung ( [EU]{ORG→O} ) 2016 / 679 )  [Single-Digital-Gateway-Verordnung]{OTH→OTH pred=„Single-Digital-Gateway-Verordnung ( Verordnung ( EU ) 2018 / 1724 )“} ( Verordnung ( [EU]{ORG→O} ) 2018 / 1724 ) Die Verordnungen gelten gemäß Art .
- `studienheft-19`: So sollte zum Beispiel durch Verabschiedung und Inkrafttreten des [Gesetzes zur Verbesserung des Onlinezugangs zu Verwaltungsleistungen]{OTH} ( [Onlinezugangsgesetz]{OTH} – [OZG]{O→OTH} ) sowie des [Bundesgesetzes zur Förderung der elektronischen Verwaltung]{OTH} ( [E-Government-Gesetz]{OTH} ) die Voraussetzung dafür geschaffen bzw .
- `studienheft-20`: dazu motiviert werden , dass die [öffentliche Verwaltung]{O→ORG} den Entwicklungen unseres Zeitalters gerecht wird .
- `studienheft-21`: Hinsichtlich dieser nachstehend thematisierten rechtlichen Grundlagen kann hier auch auf die [elektronische Lerneinheit]{O→OTH} verwiesen werden , die sich als Video mit den legislativen Grundlagen von Digitalisierung und E-Government intensiv beschäftigt .
- `studienheft-24`: Gleiches gilt für die [E-Government-Gesetze der Länder]{O→OTH} sowie das [Registermodernisierungsgesetz]{OTH} .
