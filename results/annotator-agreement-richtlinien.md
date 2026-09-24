# Annotator-Uebereinstimmung (Studienheft-Sample)

- Gemeinsam annotierte Saetze: **20**
- Spans: 15 (A) gegen 20 (B)
- **Span-F1 (exakte Grenzen und Typ): 0.857**
- Cohen's Kappa je Token (BIO): 0.853 (Rohuebereinstimmung 0.989)
- Uneinige Saetze: 3 von 20

| Typ | F1 |
|---|---|
| LOC | 1.000 |
| ORG | 0.500 |
| OTH | 0.889 |

## Uneinige Saetze

**studienheft-106** – So sollen Registermodernisierungsgesetz und OZG in ihrem Zusammenspiel insbesondere sichere sowie effiziente staatliche Onlinedienste mit einfachen und nutzerfreundlichen Antragsprozessen und kurzen Bearbeitungszeiten ermöglichen .

- nur A: –
- nur B: `OZG` (OTH)

**studienheft-15** – 910 / 2014 )  Datenschutz-Grundverordnung ( Verordnung ( EU ) 2016 / 679 )  Single-Digital-Gateway-Verordnung ( Verordnung ( EU ) 2018 / 1724 ) Die Verordnungen gelten gemäß Art .

- nur A: –
- nur B: `EU` (ORG), `EU` (ORG)

**studienheft-76** – Onlinezugangsgesetz 2 . 0 Das zumeist als OZG 2 . 0 bezeichnete OZG-Änderungsgesetz ( OZGÄndG ) wurde am 14 .

- nur A: –
- nur B: `OZG` (OTH), `OZGÄndG` (OTH)
