# Fehleranalyse – `E8__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_json_rt1_s1_p2`

F1 0.825 · P 0.901 · R 0.761 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 210 |
| Typverwechslung (Grenzen richtig) | 14 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 3 |
| übersehen | 48 |
| erfunden / falsch positiv | 5 |
| Halluzinierte Kandidaten (nicht im Text) | 24 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 72 | 0 | 2 | 0 | 4 |
| MISC | 0 | 12 | 3 | 0 | 10 |
| ORG | 9 | 2 | 81 | 0 | 3 |
| PER | 0 | 1 | 0 | 46 | 31 |
| O | 0 | 5 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 72 | 2 | 0 | 0 | 4 |
| MISC | 11 | 1 | 1 | 2 | 10 |
| ORG | 81 | 11 | 0 | 0 | 3 |
| PER | 46 | 0 | 0 | 1 | 31 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-2`: [West Indian]{MISC→O} all-rounder [Phil Simmons]{PER} took four for 38 on Friday as [Leicestershire]{ORG} beat [Somerset]{ORG} by an innings and 39 runs in two days to take over at the head of the county championship .
- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC} , [Leicestershire]{ORG} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC→ORG} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
- `conll2003-validation-23`: [Tunbridge Wells]{LOC} : [Nottinghamshire]{ORG} 214 ( [P. Johnson]{PER→O} 84 ; [M. McCague]{PER→O} 4-55 ) , [Kent]{ORG} 108-3 .
