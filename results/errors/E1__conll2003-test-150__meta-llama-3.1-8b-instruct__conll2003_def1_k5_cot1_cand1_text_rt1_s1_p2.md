# Fehleranalyse – `E1__conll2003-test-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_text_rt1_s1_p2`

F1 0.921 · P 0.978 · R 0.871 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 269 |
| Typverwechslung (Grenzen richtig) | 2 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 2 |
| übersehen | 35 |
| erfunden / falsch positiv | 1 |
| Halluzinierte Kandidaten (nicht im Text) | 18 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 82 | 0 | 0 | 0 | 6 |
| MISC | 0 | 17 | 2 | 0 | 10 |
| ORG | 0 | 0 | 12 | 1 | 3 |
| PER | 1 | 0 | 0 | 159 | 16 |
| O | 0 | 1 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 82 | 0 | 0 | 0 | 6 |
| MISC | 17 | 1 | 0 | 1 | 10 |
| ORG | 12 | 0 | 0 | 1 | 3 |
| PER | 158 | 1 | 1 | 0 | 16 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-test-0`: SOCCER - [JAPAN]{LOC} GET LUCKY WIN , [CHINA]{PER→LOC} IN SURPRISE DEFEAT .
- `conll2003-test-3`: [Japan]{LOC} began the defence of their [Asian Cup]{MISC} title with a lucky 2-1 win against [Syria]{LOC→O} in a Group C championship match on Friday .
- `conll2003-test-5`: [China]{LOC} controlled most of the match and saw several chances missed until the 78th minute when [Uzbek]{MISC→O} striker [Igor Shkvyrin]{PER} took advantage of a misdirected defensive header to lob the ball over the advancing [Chinese]{MISC→O} keeper and into an empty net .
- `conll2003-test-14`: [Japan]{LOC} then laid siege to the [Syrian]{MISC} penalty area for most of the game but rarely breached the [Syrian]{MISC→ORG pred=„Syrian defence“} defence .
- `conll2003-test-19`: [Japan]{LOC} , co-hosts of the [World Cup]{MISC} in 2002 and ranked 20th in the world by [FIFA]{ORG→O} , are favourites to regain their title here .
- `conll2003-test-22`: [RUGBY UNION]{ORG→O} - [CUTTITTA]{PER} BACK FOR [ITALY]{LOC} AFTER A YEAR .
- `conll2003-test-27`: [Stefano Bordon]{PER} is out through illness and [Coste]{PER→O} said he had dropped back row [Corrado Covi]{PER} , who had been recalled for the [England]{LOC} game after five years out of the national team .
- `conll2003-test-37`: [Takuya Takagi]{PER} headed the winner in the 88th minute of the group C game after goalkeeper [Salem Bitar]{PER→O} spoiled a mistake-free display by allowing the ball to slip under his body .
- `conll2003-test-48`: FREESTYLE [SKIING-WORLD CUP]{MISC→O} MOGUL RESULTS .
- `conll2003-test-50`: Results of the [World Cup]{MISC→ORG}
