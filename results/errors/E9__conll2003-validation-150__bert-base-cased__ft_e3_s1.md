# Fehleranalyse – `E9__conll2003-validation-150__bert-base-cased__ft_e3_s1`

F1 0.951 · P 0.946 · R 0.957 · Modell `bert-base-cased`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 264 |
| Typverwechslung (Grenzen richtig) | 2 |
| Grenzfehler (Typ richtig) | 4 |
| Grenz- und Typfehler | 2 |
| übersehen | 4 |
| erfunden / falsch positiv | 7 |
| Halluzinierte Kandidaten (nicht im Text) | 0 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | MISC | ORG | PER | O |
|---|---|---|---|---|---|
| LOC | 77 | 0 | 0 | 1 | 0 |
| MISC | 0 | 22 | 1 | 0 | 2 |
| ORG | 0 | 0 | 91 | 2 | 2 |
| PER | 0 | 0 | 0 | 78 | 0 |
| O | 0 | 1 | 2 | 4 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 77 | 1 | 0 | 0 | 0 |
| MISC | 22 | 0 | 0 | 1 | 2 |
| ORG | 90 | 1 | 1 | 1 | 2 |
| PER | 75 | 0 | 3 | 0 | 0 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `conll2003-validation-0`: CRICKET - [LEICESTERSHIRE]{ORG→PER} TAKE OVER AT TOP AFTER INNINGS VICTORY .
- `conll2003-validation-14`: They were held up by a gritty 84 from [Paul Johnson]{PER} but [ex-England]{MISC→O} fast bowler [Martin McCague]{PER} took four for 55 .
- `conll2003-validation-29`: CRICKET - 1997 [ASHES]{MISC→O} INTINERARY .
- `conll2003-validation-33`: starting on May 13 next year , the [Test and County Cricket Board]{ORG→ORG pred=„Test“}  · zusätzlich: [County Cricket Board]{O→ORG}
- `conll2003-validation-45`: May 15 v [Duke of Norfolk 's XI]{ORG→PER pred=„Duke of“} ( at [Arundel]{LOC} )  · zusätzlich: [Norfolk]{O→ORG}
- `conll2003-validation-88`: BASKETBALL - INTERNATIONAL [TOURNAMENT]{O→MISC} RESULT .
- `conll2003-validation-101`: SOCCER - [ROTOR]{ORG→O} FANS LOCKED OUT AFTER [VOLGOGRAD]{LOC→PER} VIOLENCE .
- `conll2003-validation-108`: BOXING - [PANAMA]{LOC} 'S [ROBERTO DURAN]{PER→PER pred=„DURAN“} FIGHTS THE SANDS OF TIME .
- `conll2003-validation-110`: [Panamanian]{MISC} boxing legend [Roberto " Hands of Stone " Duran]{PER→PER pred=„Roberto“} climbs into the ring on Saturday in another age-defying attempt to sustain his long career .  · zusätzlich: [Hands of Stone]{O→PER}, [Duran]{O→PER}
- `conll2003-validation-119`: If he loses Saturday , it could devalue his position as one of the world 's great boxers , " [Panamanian]{MISC→ORG pred=„Panamanian Boxing Association“} [Boxing Association]{ORG→O} President [Ramon Manzanares]{PER} said .
