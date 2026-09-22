# Fehleranalyse – `E8__conll2003-validation-150__meta-llama-3.1-8b-instruct__conll2003_def1_k0_cot1_cand1_text_rt0_s1_p2`

F1 0.000 · P 0.000 · R 0.000 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 0 |
| Typverwechslung (Grenzen richtig) | 0 |
| Grenzfehler (Typ richtig) | 0 |
| Grenz- und Typfehler | 0 |
| übersehen | 276 |
| erfunden / falsch positiv | 0 |
| Halluzinierte Kandidaten (nicht im Text) | 0 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 150 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 0 | 0 | 0 | 0 | 78 |
| MISC | 0 | 0 | 0 | 0 | 25 |
| ORG | 0 | 0 | 0 | 0 | 95 |
| PER | 0 | 0 | 0 | 0 | 78 |
| O | 0 | 0 | 0 | 0 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 0 | 0 | 0 | 0 | 78 |
| MISC | 0 | 0 | 0 | 0 | 25 |
| ORG | 0 | 0 | 0 | 0 | 95 |
| PER | 0 | 0 | 0 | 0 | 78 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-0` ⚠️ Format-Fehler: CRICKET - [LEICESTERSHIRE]{ORG→O} TAKE OVER AT TOP AFTER INNINGS VICTORY .
- `conll2003-validation-1` ⚠️ Format-Fehler: [LONDON]{LOC→O} 1996-08-30
- `conll2003-validation-2` ⚠️ Format-Fehler: [West Indian]{MISC→O} all-rounder [Phil Simmons]{PER→O} took four for 38 on Friday as [Leicestershire]{ORG→O} beat [Somerset]{ORG→O} by an innings and 39 runs in two days to take over at the head of the county championship .
- `conll2003-validation-3` ⚠️ Format-Fehler: Their stay on top , though , may be short-lived as title rivals [Essex]{ORG→O} , [Derbyshire]{ORG→O} and [Surrey]{ORG→O} all closed in on victory while [Kent]{ORG→O} made up for lost time in their rain-affected match against [Nottinghamshire]{ORG→O} .
- `conll2003-validation-4` ⚠️ Format-Fehler: After bowling [Somerset]{ORG→O} out for 83 on the opening morning at [Grace Road]{LOC→O} , [Leicestershire]{ORG→O} extended their first innings by 94 runs before being bowled out for 296 with [England]{LOC→O} discard [Andy Caddick]{PER→O} taking three for 83 .
- `conll2003-validation-5` ⚠️ Format-Fehler: Trailing by 213 , [Somerset]{ORG→O} got a solid start to their second innings before [Simmons]{PER→O} stepped in to bundle them out for 174 .
- `conll2003-validation-6` ⚠️ Format-Fehler: [Essex]{ORG→O} , however , look certain to regain their top spot after [Nasser Hussain]{PER→O} and [Peter Such]{PER→O} gave them a firm grip on their match against [Yorkshire]{ORG→O} at [Headingley]{LOC→O} .
- `conll2003-validation-7` ⚠️ Format-Fehler: [Hussain]{PER→O} , considered surplus to [England]{LOC→O} 's one-day requirements , struck 158 , his first championship century of the season , as [Essex]{ORG→O} reached 372 and took a first innings lead of 82 .
- `conll2003-validation-8` ⚠️ Format-Fehler: By the close [Yorkshire]{ORG→O} had turned that into a 37-run advantage but off-spinner [Such]{PER→O} had scuttled their hopes , taking four for 24 in 48 balls and leaving them hanging on 119 for five and praying for rain .
- `conll2003-validation-9` ⚠️ Format-Fehler: At the [Oval]{LOC→O} , [Surrey]{ORG→O} captain [Chris Lewis]{PER→O} , another man dumped by [England]{LOC→O} , continued to silence his critics as he followed his four for 45 on Thursday with 80 not out on Friday in the match against [Warwickshire]{ORG→O} .
