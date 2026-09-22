# Fehleranalyse – `E9__germeval14-test-all__bert-base-german-cased__ft_e3_s1`

F1 0.869 · P 0.872 · R 0.867 · Modell `bert-base-german-cased`

## Kennzahlen

| Größe | n |
|---|---|
| Sätze | 5100 |
| korrekt | 4502 |
| Typverwechslung (Grenzen richtig) | 137 |
| Grenzfehler (Typ richtig) | 146 |
| Grenz- und Typfehler | 94 |
| übersehen | 313 |
| erfunden / falsch positiv | 286 |
| Halluzinierte Kandidaten (nicht im Text) | 0 |
| Unbekannte Typnamen | 0 |
| Format-Fehler (parse_ok=false) | 0 |
| Retries | 0 |

## Verwechslungsmatrix (Zeile Gold, Spalte Pred; O = kein Span)

| Gold \ Pred | LOC | ORG | OTH | PER | O |
|---|---|---|---|---|---|
| LOC | 1586 | 26 | 5 | 13 | 76 |
| ORG | 34 | 954 | 36 | 14 | 112 |
| OTH | 5 | 39 | 542 | 19 | 92 |
| PER | 9 | 18 | 13 | 1566 | 33 |
| O | 82 | 74 | 88 | 42 | 0 |

## Fehler je Gold-Typ

| Typ | korrekt | Typ | Grenze | Grenze+Typ | übersehen |
|---|---|---|---|---|---|
| LOC | 1557 | 26 | 29 | 18 | 76 |
| ORG | 914 | 48 | 40 | 36 | 112 |
| OTH | 494 | 34 | 48 | 29 | 92 |
| PER | 1537 | 29 | 29 | 11 | 33 |

## Beispiele (max. 10; `[Text]{GOLD→PRED}`)

- `germeval14-test-0`: 1951 bis 1953 wurde der nördliche Teil als Jugendburg des [Kolpingwerkes]{OTH→O} gebaut .
- `germeval14-test-5`: Der Videohoster und die Vertreter der Autoren schieben sich gegenseitig den schwarzen [Peter]{PER→O} zu .
- `germeval14-test-19`: Mit Herzog [Przemysław II.]{PER→PER pred=„Przemysław II. von Großpolen“} von [Großpolen]{LOC→O} schloss [Mestwin]{PER} am 15. Februar 1282 im Vertrag von [Kempen]{LOC} eine „ donatio inter vivos “ ( Geschenk unter Lebenden ) und vermachte ihm sein Herzogtum .
- `germeval14-test-24`: Die ursprüngliche Apfeldiätspeise „ [d Spys]{OTH→O} “ Das ursprüngliche Birchermues ist eine Schweizer Spezialität und wurde um 1900 [Albert Wirz]{PER} Doktor [Birchers]{PER} neue Weltordnung .
- `germeval14-test-31`: Mit der Verpfändung [Stolbergs]{LOC→PER} an [Wilhelm von Nesselrode]{PER} war die Auflage verbunden , dass eine mögliche neue Burg als Offenhaus des Herzogs [von Jülich]{PER→LOC pred=„Jülich“} zu errichten sei .
- `germeval14-test-44`: Die Stadt richtete in den Gebäuden eine höhere Knabenschule ein , weshalb die Gebäude im Volksmund auch „ [Bubenkloster]{OTH→O} “ genannt wurde ( nicht zu verwechseln mit der eigentlichen Klosterschule im Stiftsbezirk ) .
- `germeval14-test-61`: Der 25jährige wird am Sonnabend in [Braunschweig]{LOC} im Rahmen der Supermittelgewichts-WM [Mario Veit]{PER} ( [Universum]{ORG→O} ) - [Joe Calzaghe]{PER} ( [Wales]{LOC} ) den zweiten Hauptkampf bestreiten .
- `germeval14-test-71`: Der größte Fund war die sogenannte Goldmaske des [Agamemnon]{PER} aus [Mykene]{LOC} , die nach heutigen Erkenntnissen allerdings nicht [Agamemnon]{PER→LOC} zugesprochen werden kann , da sie aus einer um etwa 300 Jahre früheren Ära stammt .
- `germeval14-test-75`: [Karlsruhe]{LOC} - Das [Bundesverfassungsgericht]{O→ORG} wird sein Urteil zur vorgezogenen Bundestagswahl in der Woche ab dem 22. August verkünden .
- `germeval14-test-104`: Der Kern des Wohnquartiers [Arrenberg]{LOC} wird von der [Friedrich-Ebert-Straße]{LOC} über zwei denkmalgeschützte [Wupperbrücken]{O→LOC} angebunden , die [Wupperbrücke]{O→LOC} [Pestalozzistraße]{LOC} an der gleichnamigen Schwebebahnstation und die [Wupperbrücke]{O→LOC} [Moritzstraße]{LOC} .
