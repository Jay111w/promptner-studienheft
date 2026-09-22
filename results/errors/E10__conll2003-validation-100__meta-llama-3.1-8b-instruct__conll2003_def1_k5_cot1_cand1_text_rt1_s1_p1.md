# Fehleranalyse – `E10__conll2003-validation-100__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_text_rt1_s1_p1`

F1 0.820 · P 0.924 · R 0.737 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 100 |
| korrekt | 146 |
| Typverwechslung (Grenzen richtig) | 9 |
| Grenzfehler (Typ richtig) | 2 |
| Grenz- und Typfehler | 1 |
| übersehen | 40 |
| erfunden / falsch positiv | 0 |
| Halluzinierte Kandidaten (nicht im Text) | 29 |
| Unbekannte Typnamen | 2 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 47 | 0 | 5 | 0 | 6 |
| MISC | 0 | 7 | 0 | 0 | 5 |
| ORG | 4 | 1 | 63 | 0 | 2 |
| PER | 0 | 0 | 0 | 31 | 27 |
| O | 0 | 0 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 47 | 5 | 0 | 0 | 6 |
| MISC | 6 | 0 | 1 | 0 | 5 |
| ORG | 62 | 4 | 1 | 1 | 2 |
| PER | 31 | 0 | 0 | 0 | 27 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC→O} , [Leicestershire]{ORG} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
- `conll2003-validation-23`: [Tunbridge Wells]{LOC→ORG} : [Nottinghamshire]{ORG} 214 ( [P. Johnson]{PER→O} 84 ; [M. McCague]{PER→O} 4-55 ) , [Kent]{ORG} 108-3 .
- `conll2003-validation-24`: [London]{LOC} ( [The Oval]{LOC} ) : [Warwickshire]{ORG} 195 , [Surrey]{ORG} 429-7 ( [C. Lewis]{PER→O} 80 not out , [M. Butcher]{PER→O} 70 , [G. Kersey]{PER→O} 63 , [J. Ratcliffe]{PER→O} 63 , [D. Bicknell]{PER→O} 55 ) .
- `conll2003-validation-25`: [Hove]{LOC} : [Sussex]{ORG→LOC} 363 ( [W. Athey]{PER→O} 111 , [V. Drakes]{PER→O} 52 ; [I. Austin]{PER→O} 4-37 ) , [Lancashire]{ORG→LOC} 197-8 ( [W. Hegg]{PER→O} 54 )
