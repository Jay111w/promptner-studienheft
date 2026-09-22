# Fehleranalyse – `E6__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k0_cot1_cand1_text_rt1_s1_p2`

F1 0.625 · P 0.663 · R 0.591 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 163 |
| Typverwechslung (Grenzen richtig) | 35 |
| Grenzfehler (Typ richtig) | 6 |
| Grenz- und Typfehler | 3 |
| übersehen | 69 |
| erfunden / falsch positiv | 39 |
| Halluzinierte Kandidaten (nicht im Text) | 25 |
| Unbekannte Typnamen | 15 |
| Format-Fehler (parse_ok=false) | 8 |
| Retries | 75 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 62 | 0 | 3 | 0 | 13 |
| MISC | 0 | 11 | 5 | 0 | 9 |
| ORG | 30 | 0 | 48 | 0 | 17 |
| PER | 0 | 0 | 0 | 48 | 30 |
| O | 11 | 20 | 3 | 5 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 61 | 3 | 1 | 0 | 13 |
| MISC | 9 | 2 | 2 | 3 | 9 |
| ORG | 46 | 30 | 2 | 0 | 17 |
| PER | 47 | 0 | 1 | 0 | 30 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-0`: [CRICKET]{O→MISC} - [LEICESTERSHIRE]{ORG} TAKE OVER AT TOP AFTER INNINGS VICTORY .
- `conll2003-validation-4`: After bowling [Somerset]{ORG} out for 83 on the opening morning at [Grace Road]{LOC} , [Leicestershire]{ORG→LOC} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC} discard [Andy Caddick]{PER} taking three for 83 .
- `conll2003-validation-7`: [Hussain]{PER→O} , considered surplus to [England]{LOC} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8`: By the close [Yorkshire]{ORG→LOC} had turned that into a 37-run advantage but off-spinner [Such]{PER} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9`: At the [Oval]{LOC→O} , [Surrey]{ORG} captain [Chris Lewis]{PER} , another man dumped by [England]{LOC→ORG} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG} .
- `conll2003-validation-10`: He was well backed by [England]{LOC→O} hopeful [Mark Butcher]{PER→O} who made 70 as [Surrey]{ORG→O} closed on 429 for seven , a lead of 234 .
- `conll2003-validation-11`: [Derbyshire]{ORG→O} kept up the hunt for their first championship title since 1936 by reducing [Worcestershire]{ORG→O} to 133 for five in their second innings , still 100 runs away from avoiding an innings defeat .
- `conll2003-validation-12`: [Australian]{MISC} [Tom Moody]{PER} took six for 82 but [Chris Adams]{PER} , 123 , and [Tim O'Gorman]{PER} , 109 , took [Derbyshire]{ORG→LOC} to 471 and a first innings lead of 233 .
- `conll2003-validation-13`: After the frustration of seeing the opening day of their match badly affected by the weather , [Kent]{ORG→LOC} stepped up a gear to dismiss [Nottinghamshire]{ORG→LOC} for 214 .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
