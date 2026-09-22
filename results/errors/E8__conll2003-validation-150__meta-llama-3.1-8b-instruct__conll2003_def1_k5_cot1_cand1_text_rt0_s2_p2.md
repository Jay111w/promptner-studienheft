# Fehleranalyse – `E8__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand1_text_rt0_s2_p2`

F1 0.817 · P 0.907 · R 0.743 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 205 |
| Typverwechslung (Grenzen richtig) | 14 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 3 |
| übersehen | 53 |
| erfunden / falsch positiv | 3 |
| Halluzinierte Kandidaten (nicht im Text) | 31 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 72 | 0 | 0 | 0 | 6 |
| MISC | 0 | 10 | 3 | 0 | 12 |
| ORG | 12 | 1 | 78 | 1 | 3 |
| PER | 0 | 0 | 0 | 46 | 32 |
| O | 1 | 1 | 1 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 72 | 0 | 0 | 0 | 6 |
| MISC | 10 | 2 | 0 | 1 | 12 |
| ORG | 77 | 12 | 1 | 2 | 3 |
| PER | 46 | 0 | 0 | 0 | 32 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-19`: [Leicester]{LOC} : [Leicestershire]{ORG→LOC} beat [Somerset]{ORG→LOC} by an innings and 39 runs .
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
- `conll2003-validation-23`: [Tunbridge Wells]{LOC} : [Nottinghamshire]{ORG} 214 ( [P. Johnson]{PER→O} 84 ; [M. McCague]{PER→O} 4-55 ) , [Kent]{ORG} 108-3 .
- `conll2003-validation-24`: [London]{LOC} ( [The Oval]{LOC} ) : [Warwickshire]{ORG} 195 , [Surrey]{ORG} 429-7 ( [C. Lewis]{PER→O} 80 not out , [M. Butcher]{PER→O} 70 , [G. Kersey]{PER→O} 63 , [J. Ratcliffe]{PER→O} 63 , [D. Bicknell]{PER→O} 55 ) .
