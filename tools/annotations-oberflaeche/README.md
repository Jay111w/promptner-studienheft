# Annotations-Oberfläche

Die Klick-Oberfläche, mit der die Studienheft-Sätze beschriftet werden, statt JSON von Hand zu
bearbeiten. Sie ist eine einzelne HTML-Seite ohne Server und lässt sich direkt im Browser öffnen
oder über einen beliebigen statischen Webserver ausliefern.

## Die zwei Dateien

`annotation.html` ist die Seite selbst, ohne Abhängigkeiten außer den Schriften von Google Fonts.
`saetze.json` liefert ihr die Sätze und ist aus den drei Dateien in `data/studienheft/` erzeugt:
der gemeinsame Block ohne Vorschläge, die beiden persönlichen Blöcke mit den Vorschlägen des
Modells.

## Neu erzeugen

Wenn sich die Vorlage ändert, entsteht `saetze.json` so:

```python
import json
from promptner.data import load_jsonl

base = "data/studienheft"
pack = lambda sents, block, owner: {
    "block": block,
    "owner": owner,
    "saetze": [
        {
            "id": s.id,
            "tokens": s.tokens,
            "vorschlag": [{"start": sp.start, "end": sp.end, "label": sp.label} for sp in s.spans],
        }
        for s in sents
    ],
}
out = {"blocks": [
    pack(load_jsonl(f"{base}/gold_gemeinsam_VORLAGE.jsonl"), "gemeinsam", None),
    pack(load_jsonl(f"{base}/vorschlag_joshua.jsonl"), "persoenlich", "joshua"),
    pack(load_jsonl(f"{base}/vorschlag_alireza.jsonl"), "persoenlich", "alireza"),
]}
with open("tools/annotations-oberflaeche/saetze.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
```

Danach liegen beide Dateien nebeneinander im selben Verzeichnis, `saetze.json` unter genau diesem
Namen, weil die Seite sie relativ zu sich selbst lädt.

## Wo die Arbeit liegt

Im `localStorage` des jeweiligen Browsers, je Annotator ein Eintrag. Das ist Absicht, denn eine
gemeinsame Datenbank hätte einen Server verlangt, und die beiden Annotatoren arbeiten ohnehin an
verschiedenen Rechnern. Der Nebeneffekt passt zur Methodik, weil der gemeinsame Block unabhängig
bearbeitet werden muss.

Der Preis ist der Rückweg: Über „Als Datei sichern“ oder „In die Zwischenablage“ gibt jeder seinen
Stand als JSON heraus, das dann zu `gold_<name>.jsonl` und `gold_gemeinsam_<name>.jsonl` wird.
Das ausgegebene Format trägt je Satz `id`, `block`, `erledigt`, `tokens` und `spans`.
