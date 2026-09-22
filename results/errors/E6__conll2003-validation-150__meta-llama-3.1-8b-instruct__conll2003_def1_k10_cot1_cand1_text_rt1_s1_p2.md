# Fehleranalyse – `E6__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k10_cot1_cand1_text_rt1_s1_p2`

F1 0.805 · P 0.873 · R 0.746 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 206 |
| Typverwechslung (Grenzen richtig) | 21 |
| Grenzfehler (Typ richtig) | 3 |
| Grenz- und Typfehler | 2 |
| übersehen | 44 |
| erfunden / falsch positiv | 4 |
| Halluzinierte Kandidaten (nicht im Text) | 30 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 70 | 0 | 2 | 0 | 6 |
| MISC | 0 | 17 | 1 | 0 | 7 |
| ORG | 10 | 10 | 74 | 0 | 1 |
| PER | 0 | 0 | 0 | 48 | 30 |
| O | 1 | 3 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 70 | 2 | 0 | 0 | 6 |
| MISC | 15 | 0 | 2 | 1 | 7 |
| ORG | 73 | 19 | 1 | 1 | 1 |
| PER | 48 | 0 | 0 | 0 | 30 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC} , [Leicestershire]{ORG} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC→ORG} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-10`: He was well backed by [England]{LOC→O} hopeful [Mark Butcher]{PER} who made 70 as [Surrey]{ORG} closed on 429 for seven , a lead of 234 .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-19`: [Leicester]{LOC} : [Leicestershire]{ORG→LOC} beat [Somerset]{ORG→LOC} by an innings and 39 runs .
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
- `conll2003-validation-23`: [Tunbridge Wells]{LOC} : [Nottinghamshire]{ORG} 214 ( [P. Johnson]{PER→O} 84 ; [M. McCague]{PER→O} 4-55 ) , [Kent]{ORG} 108-3 .
