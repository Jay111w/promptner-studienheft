# Fehleranalyse – `E3__conll2003-validation-150__qwen3.5-397b-a17b__conll2003_def1_k5_cot1_cand1_text_rt1_s1_p2`

F1 0.896 · P 0.959 · R 0.841 · Modell `qwen3.5-397b-a17b`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 232 |
| Typverwechslung (Grenzen richtig) | 7 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 2 |
| übersehen | 34 |
| erfunden / falsch positiv | 0 |
| Halluzinierte Kandidaten (nicht im Text) | 31 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 68 | 0 | 6 | 0 | 4 |
| MISC | 0 | 22 | 1 | 0 | 2 |
| ORG | 1 | 1 | 91 | 0 | 2 |
| PER | 0 | 0 | 0 | 52 | 26 |
| O | 0 | 0 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 68 | 6 | 0 | 0 | 4 |
| MISC | 21 | 0 | 1 | 1 | 2 |
| ORG | 91 | 1 | 0 | 1 | 2 |
| PER | 52 | 0 | 0 | 0 | 26 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-7`: [Hussain]{PER} , considered surplus to [England]{LOC→ORG} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-9`: At the [Oval]{LOC} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-10`: He was well backed by [England]{LOC→O} hopeful [Mark Butcher]{PER} who made 70 as [Surrey]{ORG} closed on 429 for seven , a lead of 234 .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
- `conll2003-validation-22`: [Chester-le-Street]{LOC} : [Glamorgan]{ORG} 259 and 207 ( [A. Dale]{PER→O} 69 , [H. Morris]{PER→O} 69 ; [D. Blenkiron]{PER→O} 4-43 ) , [Durham]{ORG} 114 ( [S. Watkin]{PER→O} 4-28 ) and 81-3 .
- `conll2003-validation-23`: [Tunbridge Wells]{LOC} : [Nottinghamshire]{ORG} 214 ( [P. Johnson]{PER→O} 84 ; [M. McCague]{PER→O} 4-55 ) , [Kent]{ORG} 108-3 .
- `conll2003-validation-24`: [London]{LOC} ( [The Oval]{LOC} ) : [Warwickshire]{ORG} 195 , [Surrey]{ORG} 429-7 ( [C. Lewis]{PER→O} 80 not out , [M. Butcher]{PER→O} 70 , [G. Kersey]{PER→O} 63 , [J. Ratcliffe]{PER→O} 63 , [D. Bicknell]{PER→O} 55 ) .
- `conll2003-validation-25`: [Hove]{LOC} : [Sussex]{ORG} 363 ( [W. Athey]{PER→O} 111 , [V. Drakes]{PER→O} 52 ; [I. Austin]{PER→O} 4-37 ) , [Lancashire]{ORG} 197-8 ( [W. Hegg]{PER→O} 54 )
- `conll2003-validation-26`: [Portsmouth]{LOC} : [Middlesex]{ORG} 199 and 426 ( [J. Pooley]{PER→O} 111 , [M. Ramprakash]{PER→O} 108 , [M. Gatting]{PER→O} 83 ) , [Hampshire]{ORG} 232 and 109-5 .
