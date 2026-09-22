# Fehleranalyse – `E7__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k5_cot1_cand0_text_s1_p2`

F1 0.825 · P 0.940 · R 0.736 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 203 |
| Typverwechslung (Grenzen richtig) | 11 |
| Grenzfehler (Typ richtig) | 1 |
| Grenz- und Typfehler | 1 |
| übersehen | 60 |
| erfunden / falsch positiv | 0 |
| Halluzinierte Kandidaten (nicht im Text) | 34 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 66 | 0 | 4 | 0 | 8 |
| MISC | 0 | 10 | 1 | 0 | 14 |
| ORG | 7 | 0 | 84 | 0 | 4 |
| PER | 0 | 0 | 0 | 44 | 34 |
| O | 0 | 0 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 66 | 4 | 0 | 0 | 8 |
| MISC | 9 | 0 | 1 | 1 | 14 |
| ORG | 84 | 7 | 0 | 0 | 4 |
| PER | 44 | 0 | 0 | 0 | 34 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-5`: Trailing by 213 , [Somerset]{ORG} got a solid start to their second innings before [Simmons]{PER→O} stepped in to bundle them out for 174 .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC→O} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8`: By the close [Yorkshire]{ORG} had turned that into a 37-run advantage but off-spinner [Such]{PER→O} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-10`: He was well backed by [England]{LOC→ORG} hopeful [Mark Butcher]{PER} who made 70 as [Surrey]{ORG} closed on 429 for seven , a lead of 234 .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-15`: By stumps [Kent]{ORG→O} had reached 108 for three .
- `conll2003-validation-16`: CRICKET - [ENGLISH COUNTY CHAMPIONSHIP]{MISC→O} SCORES .
- `conll2003-validation-18`: Result and close of play scores in [English]{MISC→O} county championship matches on Friday :
- `conll2003-validation-19`: [Leicester]{LOC→ORG} : [Leicestershire]{ORG} beat [Somerset]{ORG} by an innings and 39 runs .
