# Fehleranalyse – `E1__germeval14-test-150__meta-llama-3.1-8b-instruct__germeval14_def1_k5_cot1_cand1_text_rt1_s1_p2`

F1 0.687 · P 0.681 · R 0.694 · Modell `meta-llama-3.1-8b-instruct`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 150 |
| korrekt | 111 |
| Typverwechslung (Grenzen richtig) | 9 |
| Grenzfehler (Typ richtig) | 7 |
| Grenz- und Typfehler | 5 |
| übersehen | 28 |
| erfunden / falsch positiv | 31 |
| Halluzinierte Kandidaten (nicht im Text) | 17 |
| Unbekannte Typnamen | 1 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 40 | 0 | 2 | 0 | 5 |
| ORG | 1 | 21 | 7 | 0 | 9 |
| OTH | 0 | 1 | 8 | 1 | 6 |
| PER | 1 | 0 | 1 | 49 | 8 |
| O | 11 | 1 | 18 | 1 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 36 | 0 | 4 | 2 | 5 |
| ORG | 20 | 8 | 1 | 0 | 9 |
| OTH | 8 | 1 | 0 | 1 | 6 |
| PER | 47 | 0 | 2 | 2 | 8 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `germeval14-test-0`: 1951 bis 1953 wurde der nördliche Teil als Jugendburg des [Kolpingwerkes]{OTH→O} gebaut .
- `germeval14-test-1`: Da [Muck]{PER→O} das Kriegsschreiben nicht überbracht hat , wird er als Retter des Landes ausgezeichnet und soll zum Schatzmeister ernannt werden .
- `germeval14-test-4`: " [Lehmbruck - Beuys .Zeichnungen]{OTH→PER pred=„Lehmbruck“} " lautet der Titel der gerade eröffneten Ausstellung , die Kuratorin Dr . [Marion Bornscheuer]{PER→PER pred=„Dr . Marion Bornscheuer“} bis zum 11. Januar im [Lehmbruck-Museum]{ORG→LOC} präsentiert .  · zusätzlich: [Beuys]{O→PER}
- `germeval14-test-5`: Der Videohoster und die Vertreter der Autoren schieben sich gegenseitig den schwarzen [Peter]{PER→O} zu .
- `germeval14-test-6`: Die [Kanzel]{O→OTH} befindet sich an der Südseite des Saals .
- `germeval14-test-8`: Nach den Symptomen lassen sich die beiden Krankheiten - " normale " [Influenza]{O→OTH} und [Schweinegrippe]{O→OTH} - nicht unterscheiden .
- `germeval14-test-10`: Am 20. Januar 1839 gelang [Manuel Bulnes]{PER} bei der Belagerung von [Yungay]{LOC→OTH pred=„Belagerung von Yungay“} der entscheidende Sieg .
- `germeval14-test-17`: Heute ist durch einen roten Ziegelstreifen der Verlauf [des an den Turm anschließenden nordwestlichen Mauerrings]{O→LOC} gekennzeichnet , während der südwestliche Mauerring bis zum Gelände des ehemaligen Franziskanerklosters [St . Johannis]{LOC} noch intakt ist .
- `germeval14-test-19`: Mit Herzog [Przemysław II.]{PER→O} von [Großpolen]{LOC→O} schloss [Mestwin]{PER} am 15. Februar 1282 im Vertrag von [Kempen]{LOC→OTH pred=„Vertrag von Kempen“} eine „ donatio inter vivos “ ( Geschenk unter Lebenden ) und vermachte ihm sein Herzogtum .
- `germeval14-test-21`: Die [London Telegram]{ORG→OTH} vom 21. Januar 1914 berichtete , dass [Karl Richter]{PER} wegen des Diebstahls der belastenden Papiere und der versuchten Erpressung seines Arbeitgebers , in [Deutschland]{LOC} zu 2 Jahren Gefängnis verurteilt wurde .
