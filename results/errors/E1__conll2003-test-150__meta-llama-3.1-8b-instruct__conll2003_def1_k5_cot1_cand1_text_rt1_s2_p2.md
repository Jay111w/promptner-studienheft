# Fehleranalyse – `E1__conll2003-test-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_text_rt1_s2_p2`

F1 0.924 · P 0.985 · R 0.871 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 269 |
| Typverwechslung (Grenzen richtig) | 3 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 0 |
| übersehen | 36 |
| erfunden / falsch positiv | 0 |
| Halluzinierte Kandidaten (nicht im Text) | 15 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 83 | 0 | 0 | 0 | 5 |
| MISC | 0 | 15 | 2 | 0 | 12 |
| ORG | 0 | 0 | 14 | 0 | 2 |
| PER | 1 | 0 | 0 | 158 | 17 |
| O | 0 | 0 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 83 | 0 | 0 | 0 | 5 |
| MISC | 15 | 2 | 0 | 0 | 12 |
| ORG | 14 | 0 | 0 | 0 | 2 |
| PER | 157 | 1 | 1 | 0 | 17 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-test-0`: SOCCER - [JAPAN]{LOC} GET LUCKY WIN , [CHINA]{PER→LOC} IN SURPRISE DEFEAT .
- `conll2003-test-5`: [China]{LOC} controlled most of the match and saw several chances missed until the 78th minute when [Uzbek]{MISC→O} striker [Igor Shkvyrin]{PER} took advantage of a misdirected defensive header to lob the ball over the advancing [Chinese]{MISC} keeper and into an empty net .
- `conll2003-test-8`: Despite winning the [Asian Games]{MISC→O} title two years ago , [Uzbekistan]{LOC} are in the finals as outsiders .
- `conll2003-test-17`: The [Syrians]{MISC→O} scored early and then played defensively and adopted long balls which made it hard for us . '
- `conll2003-test-19`: [Japan]{LOC} , co-hosts of the [World Cup]{MISC→O} in 2002 and ranked 20th in the world by [FIFA]{ORG} , are favourites to regain their title here .
- `conll2003-test-22`: [RUGBY UNION]{ORG→O} - [CUTTITTA]{PER} BACK FOR [ITALY]{LOC} AFTER A YEAR .
- `conll2003-test-27`: [Stefano Bordon]{PER} is out through illness and [Coste]{PER→O} said he had dropped back row [Corrado Covi]{PER} , who had been recalled for the [England]{LOC} game after five years out of the national team .
- `conll2003-test-28`: [Cuttitta]{PER} announced his retirement after the [1995 World Cup]{MISC→O} , where he took issue with being dropped from the [Italy]{LOC} side that faced [England]{LOC} in the pool stages .
- `conll2003-test-30`: " He ended the [World Cup]{MISC} on the wrong note , " [Coste]{PER→O} said .
- `conll2003-test-36`: Two goals in the last six minutes gave holders [Japan]{LOC} an uninspiring 2-1 [Asian Cup]{MISC→ORG} victory over [Syria]{LOC} on Friday .
