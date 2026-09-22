# Fehleranalyse – `E5__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot0_cand1_text_s1_p2`

F1 0.784 · P 0.865 · R 0.717 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 198 |
| Typverwechslung (Grenzen richtig) | 21 |
| Grenzfehler (Typ richtig) | 3 |
| Grenz- und Typfehler | 2 |
| übersehen | 52 |
| erfunden / falsch positiv | 5 |
| Halluzinierte Kandidaten (nicht im Text) | 22 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 58 | 1 | 13 | 0 | 6 |
| MISC | 0 | 14 | 1 | 0 | 10 |
| ORG | 7 | 1 | 85 | 0 | 2 |
| PER | 0 | 0 | 0 | 44 | 34 |
| O | 2 | 3 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 58 | 13 | 0 | 1 | 6 |
| MISC | 12 | 0 | 2 | 1 | 10 |
| ORG | 84 | 8 | 1 | 0 | 2 |
| PER | 44 | 0 | 0 | 0 | 34 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC} , [Leicestershire]{ORG} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC→ORG} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC→ORG} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8`: By the close [Yorkshire]{ORG} had turned that into a 37-run advantage but off-spinner [Such]{PER→O} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-10`: He was well backed by [England]{LOC→ORG} hopeful [Mark Butcher]{PER} who made 70 as [Surrey]{ORG} closed on 429 for seven , a lead of 234 .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
