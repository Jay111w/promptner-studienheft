# Fehleranalyse – `E6__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k2_cot1_cand1_text_rt1_s1_p2`

F1 0.780 · P 0.881 · R 0.699 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 193 |
| Typverwechslung (Grenzen richtig) | 19 |
| Grenzfehler (Typ richtig) | 3 |
| Grenz- und Typfehler | 1 |
| übersehen | 60 |
| erfunden / falsch positiv | 3 |
| Halluzinierte Kandidaten (nicht im Text) | 31 |
| Unbekannte Typnamen | 6 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 70 | 0 | 0 | 0 | 8 |
| MISC | 0 | 9 | 1 | 0 | 15 |
| ORG | 19 | 0 | 71 | 0 | 5 |
| PER | 0 | 0 | 0 | 46 | 32 |
| O | 1 | 2 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 69 | 0 | 1 | 0 | 8 |
| MISC | 8 | 0 | 1 | 1 | 15 |
| ORG | 70 | 19 | 1 | 0 | 5 |
| PER | 46 | 0 | 0 | 0 | 32 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-6`: [Essex]{ORG} , however , look certain to regain their top spot after [Nasser Hussain]{PER} and [Peter Such]{PER} gave them a firm grip on their match against [Yorkshire]{ORG} at [Headingley]{LOC→O} .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC→O} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8`: By the close [Yorkshire]{ORG} had turned that into a 37-run advantage but off-spinner [Such]{PER→O} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9`: At the [Oval]{LOC→LOC pred=„the Oval“} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-15`: By stumps [Kent]{ORG→LOC} had reached 108 for three .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-19`: [Leicester]{LOC} : [Leicestershire]{ORG→LOC} beat [Somerset]{ORG→LOC} by an innings and 39 runs .
- `conll2003-validation-20`: [Somerset]{ORG} 83 and 174 ( [P. Simmons]{PER→O} 4-38 ) , [Leicestershire]{ORG} 296 .
