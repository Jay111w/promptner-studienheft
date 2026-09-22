# Fehleranalyse – `E9__conll2003-test-all__bert-base-cased__ft_e3_s1`

F1 0.915 · P 0.911 · R 0.920 · Modell `bert-base-cased`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 3453 |
| korrekt | 5198 |
| Typverwechslung (Grenzen richtig) | 230 |
| Grenzfehler (Typ richtig) | 60 |
| Grenz- und Typfehler | 60 |
| übersehen | 100 |
| erfunden / falsch positiv | 160 |
| Halluzinierte Kandidaten (nicht im Text) | 0 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 1554 | 27 | 58 | 9 | 20 |
| MISC | 22 | 602 | 37 | 7 | 34 |
| ORG | 44 | 33 | 1541 | 16 | 27 |
| PER | 12 | 1 | 24 | 1561 | 19 |
| O | 19 | 55 | 66 | 20 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 1548 | 71 | 6 | 23 | 20 |
| MISC | 575 | 54 | 27 | 12 | 34 |
| ORG | 1521 | 70 | 20 | 23 | 27 |
| PER | 1554 | 35 | 7 | 2 | 19 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-test-0`: SOCCER - [JAPAN]{LOC→ORG} GET [LUCKY]{O→PER} WIN , [CHINA]{PER} IN SURPRISE DEFEAT .
- `conll2003-test-22`: [RUGBY UNION]{ORG} - [CUTTITTA]{PER→LOC} BACK FOR [ITALY]{LOC→ORG} AFTER A YEAR .
- `conll2003-test-28`: [Cuttitta]{PER} announced his retirement after the [1995 World Cup]{MISC→MISC pred=„World Cup“} , where he took issue with being dropped from the [Italy]{LOC} side that faced [England]{LOC} in the pool stages .
- `conll2003-test-34`: SOCCER - LATE GOALS GIVE [JAPAN]{LOC→PER} WIN OVER [SYRIA]{LOC} .
- `conll2003-test-74`: SOCCER - [ASIAN CUP]{MISC→MISC pred=„ASIAN CUP GROUP“} GROUP C RESULTS .
- `conll2003-test-91`: CRICKET - [PAKISTAN]{LOC} V [NEW ZEALAND]{LOC→LOC pred=„ZEALAND“} ONE-DAY SCOREBOARD .
- `conll2003-test-137`: SOCCER - [ENGLISH F.A. CUP]{MISC→MISC pred=„ENGLISH“} SECOND ROUND RESULT .  · zusätzlich: [F.A. CUP]{O→MISC}
- `conll2003-test-139`: Result of an [English F.A. Challenge]{MISC→MISC pred=„English“}  · zusätzlich: [F.A. Challenge]{O→MISC}
- `conll2003-test-148`: [Blinker]{PER} was fined 75,000 [Swiss]{MISC} francs ( $ 57,600 ) for failing to inform the [Engllsh]{MISC→ORG} club of his previous commitment to [Udinese]{ORG} .
- `conll2003-test-149`: SOCCER - [LEEDS]{ORG→PER} ' [BOWYER]{PER→O} FINED FOR PART IN FAST-FOOD [FRACAS]{O→ORG} .
