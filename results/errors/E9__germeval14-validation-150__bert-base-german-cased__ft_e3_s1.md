# Fehleranalyse – `E9__germeval14-validation-150__bert-base-german-cased__ft_e3_s1`

F1 0.907 · P 0.910 · R 0.904 · Modell `bert-base-german-cased`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 141 |
| Typverwechslung (Grenzen richtig) | 3 |
| Grenzfehler (Typ richtig) | 4 |
| Grenz- und Typfehler | 3 |
| übersehen | 5 |
| erfunden / falsch positiv | 4 |
| Halluzinierte Kandidaten (nicht im Text) | 0 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 57 | 0 | 0 | 1 | 0 |
| ORG | 2 | 28 | 1 | 1 | 3 |
| OTH | 0 | 0 | 21 | 0 | 2 |
| PER | 0 | 1 | 0 | 39 | 0 |
| O | 0 | 1 | 2 | 1 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 57 | 1 | 0 | 0 | 0 |
| ORG | 25 | 2 | 3 | 2 | 3 |
| OTH | 20 | 0 | 1 | 0 | 2 |
| PER | 39 | 0 | 0 | 1 | 0 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `germeval14-validation-8`: Der sechste Lauf der [ADAC GT]{ORG→ORG pred=„ADAC GT Mastersstand“} Mastersstand ganz klar im Mittelpunkt des Motorsport-Wochenendes auf dem [Eurospeedway Lausitz]{ORG→LOC} .
- `germeval14-validation-9`: Nach den schwächeren Vorgaben der [Wall Street]{ORG→OTH pred=„Wall“} vom Vortag setzten die deutschen Standardwerte ihren Konsolidierungskurs fort .  · zusätzlich: [Street]{O→ORG}
- `germeval14-validation-35`: Der [Reichsvereinigung der Juden in Deutschland]{ORG→LOC pred=„Deutschland“} waren zahlreiche Gebäude überschrieben worden , weil kleinere Kultusgemeinden den Unterhalt nicht mehr finanzieren konnten oder sich auflösten .
- `germeval14-validation-56`: [Weinkauf]{O→PER} wird gleichzeitig zum Architekturtrip .
- `germeval14-validation-64`: Von 1920 bis 1927 war sie zudem Vorsitzende des „ [Verbandes Norddeutscher Frauenvereine]{ORG} “ und war maßgeblich an dem Zusammenschluss der [Hamburger Frauenverbände]{ORG→O} zur „ [Hamburger Frauenhilfe]{ORG} “ beteiligt .
- `germeval14-validation-66`: [Vom Lesen und Schreiben des Menschen - Literaturgeschichten der Moderne]{OTH→OTH pred=„Moderne“} .
- `germeval14-validation-79`: Die Stammreihe beginnt mit [Odobaldus]{PER} , erster Herr von [Werthern]{LOC→PER} .
- `germeval14-validation-83`: Auch [Kraftwerk]{ORG→O} dürfte bleibende Eindrücke hinterlassen haben .
- `germeval14-validation-88`: Einer von vielen Nachteilen dürfte die fehlende Anschaltung von Rundumtonkombination an zukünftige [BOSNET]{OTH→O} MobilGeräte , oder die Austauschbarkeit von Sprechgarnituren bei Handfunkgeräten sein .
- `germeval14-validation-103`: Der [Oberste Gerichtshof]{ORG→O} [Kanadas]{LOC} urteilte 1997 , dass diese Beschränkung zu streng sei und dem Grundsatz der Meinungsfreiheit in der Charta der Rechte und Freiheiten widerspreche .
