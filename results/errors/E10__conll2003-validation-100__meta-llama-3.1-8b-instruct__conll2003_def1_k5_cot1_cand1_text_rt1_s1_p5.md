# Fehleranalyse – `E10__conll2003-validation-100__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_text_rt1_s1_p5`

F1 0.722 · P 0.883 · R 0.611 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 100 |
| korrekt | 121 |
| Typverwechslung (Grenzen richtig) | 14 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 0 |
| übersehen | 62 |
| erfunden / falsch positiv | 1 |
| Halluzinierte Kandidaten (nicht im Text) | 24 |
| Unbekannte Typnamen | 8 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 41 | 0 | 2 | 0 | 15 |
| MISC | 0 | 4 | 0 | 0 | 8 |
| ORG | 12 | 0 | 52 | 0 | 6 |
| PER | 0 | 0 | 0 | 25 | 33 |
| O | 0 | 1 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 41 | 2 | 0 | 0 | 15 |
| MISC | 4 | 0 | 0 | 0 | 8 |
| ORG | 51 | 12 | 1 | 0 | 6 |
| PER | 25 | 0 | 0 | 0 | 33 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC} , [Leicestershire]{ORG} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC→O} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-6`: [Essex]{ORG} , however , look certain to regain their top spot after [Nasser Hussain]{PER} and [Peter Such]{PER} gave them a firm grip on their match against [Yorkshire]{ORG} at [Headingley]{LOC→O} .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8`: By the close [Yorkshire]{ORG} had turned that into a 37-run advantage but off-spinner [Such]{PER→O} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC→O} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
