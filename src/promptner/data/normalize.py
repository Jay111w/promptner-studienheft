"""Die Annotationsrichtlinien maschinell auf annotierte Saetze anwenden.

Warum es diesen Schritt gibt: Die Uebereinstimmung der beiden Annotatoren lag bei Span-F1 0.489.
Die Liste der uneinigen Saetze zeigt, dass das keine Streuung zweier Urteile ist, sondern drei
systematische Abweichungen von ``data/studienheft/ANNOTATION.md`` — und zwar bei beiden:

1. **Gattungsbegriffe als Entitaet.** Die Richtlinie sagt "Nur Eigennamen, keine Gattungsbegriffe"
   und nennt ``der Bund``, ``die Behoerde``, ``das Gesetz`` ausdruecklich als Nicht-Entitaeten.
   Annotiert wurden trotzdem ``Vision``, ``Erwartungshaltung``, ``Verwaltungsleistungen``,
   ``Bund`` (einmal ORG, einmal LOC), ``Laender``, ``Behoerden``.
2. **Grenzen mit Modifikator.** Die Richtlinie schliesst Artikel aus und erklaert Ableitungen zu
   Nicht-Entitaeten. Annotiert wurde teils ``rechtlichen Grundlagen`` statt ``Grundlagen``,
   ``staatliche Onlinedienste`` statt ``Onlinedienste``.
3. **Rollenbezeichnungen als PER.** Die Richtlinie sagt zu PER ausdruecklich "nicht: die
   Bundeskanzlerin". Annotiert wurde ``Buergerinnen`` / ``Buergern`` als PER.

Weil die Richtlinien **vor** der Annotation festgelegt waren, ist ihre Durchsetzung keine neue
Urteilsrunde, sondern eine Korrektur der Anwendung. Sie laeuft deterministisch und fuer beide
Annotatoren identisch, also ohne die Uebereinstimmung in eine Richtung zu schieben.

Was das nicht ist: menschliche Adjudikation. Die Regeln unten sind nach Sicht der Daten
formuliert, und der Lexikonteil nennt die Eigennamen dieser Quelle beim Namen. Das gehoert so in
den Bericht, und die rohe Zahl 0.489 bleibt die Zahl, die zwei Menschen erzeugt haben.

Die Regeln folgen der Reihenfolge: erst Grenzen (``_trimme``), dann Eigennamen-Test
(``ist_eigenname``), dann Aufraeumen des Satzes (Duplikate, Ueberlappungen).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from promptner.domain import Sentence, Span

# ---------------------------------------------------------------------------
# Lexikon: die Eigennamen dieser Quelle, aus der Tabelle in ANNOTATION.md und den
# tatsaechlich vorkommenden Oberflaechenformen. Genitiv- und Pluralformen stehen mit,
# weil der Text sie flektiert ("des Bundestags").
# ---------------------------------------------------------------------------

LEX_LOC = {
    "Deutschland",
    "Europa",
    "Rheinland-Pfalz",
    "Schleswig-Holstein",
    "Hamburg",
    "Bayern",
    "Berlin",
    "Sachsen",
    "Hessen",
    "Nordrhein-Westfalen",
    "Baden-Württemberg",
    "Brandenburg",
    "Bremen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Saarland",
    "Sachsen-Anhalt",
    "Thüringen",
}

LEX_ORG = {
    "EU",
    "EU-Kommission",
    "Europäische Union",
    "Europäischen Union",
    "Europäische Kommission",
    "Bundestag",
    "Bundestags",
    "Bundesrat",
    "Bundesrats",
    "Bundesregierung",
    "Bundesministerium des Innern",
    "IT-Planungsrat",
    "IT-Planungsrats",
    "KGSt",
    "Hochschule Koblenz",
}

LEX_PER = {"Proll", "Drammeh", "Piesold"}

# Benannte Gesetze, Programme und Systeme erkennt man an diesen Bestandteilen. Der Test laeuft
# auf der kleingeschriebenen Oberflaeche, deshalb stehen die Eintraege klein.
OTH_BESTANDTEILE = (
    "gesetz",
    "verordnung",
    "vertrag",
    "richtlinie",
    "aktionsplan",
    "action plan",
    "dekade",
    "umsetzungskatalog",
    "leistungskatalog",
    "zertifikat",
    "cockpit",
    "europe",
)

# Oberflaechen, die einen Bestandteil von oben tragen, aber Gattungsbegriff bleiben: "das Gesetz",
# "ein Bundesgesetz", "die Verordnungen". ANNOTATION.md nennt genau diesen Fall.
GATTUNG = {
    "Gesetz",
    "Gesetzes",
    "Gesetze",
    "Gesetzen",
    "Gesetz des Bundes",
    "Gesetzes des Bundes",
    "Bundesgesetz",
    "Bundesgesetzes",
    "Landesgesetz",
    "Änderungsgesetz",
    "Verordnung",
    "Verordnungen",
    "E-Government-Gesetze",
    "E-Government-Gesetzen",
    "Aktionsplan",
    "Aktionsplans",
    # Ableitung statt Name: die Leistungen *nach* dem OZG heissen nicht so.
    "OZG-Leistungen",
}

# Rein grammatische Tokens am Rand eines Spans. Deutsche Eigennamen sind grossgeschrieben, deshalb
# traegt die Kleinschreibung den Test; diese Liste fasst nur, was zusaetzlich am Rand stoert.
SATZZEICHEN = set(".,;:!?()[]{}\"'„“”–—/§&")

# Ein Token gilt als Abkuerzung, wenn es zwei aufeinanderfolgende Grossbuchstaben traegt:
# OZG, DSGVO, EGovGRP, BundID, DeutschlandID. Nicht: E-Government, Ende-zu-Ende-Digitalisierung,
# deren Grossbuchstaben einzeln stehen.
ABKUERZUNG = re.compile(r"[A-ZÄÖÜ]{2}")

ZITAT_ANFANG = {"§", "§§", "Artikel", "Art", "Abs", "Absatz"}


@dataclass(frozen=True)
class Protokoll:
    """Was die Normalisierung getan hat - fuer den Bericht und zum Nachpruefen."""

    behalten: list[tuple[str, str]]
    getrimmt: list[tuple[str, str]]
    verworfen: list[tuple[str, str]]


def _ist_satzzeichen(token: str) -> bool:
    return not token or all(ch in SATZZEICHEN for ch in token)


def _ist_rand_muell(token: str) -> bool:
    """Satzzeichen, blosse Ziffern und Kleinschreibung (Artikel, Adjektive) am Rand.

    Nur am **linken** Rand angewandt: rechts kann eine Zahl zum Namen gehoeren, wie in
    "Digitale Dekade 2030" oder dem Beispiel "Olympische Spiele 2024" aus ANNOTATION.md.
    """
    if _ist_satzzeichen(token):
        return True
    if token.replace(".", "").replace(",", "").isdigit():
        return True
    return not any(ch.isupper() for ch in token)


def _trimme(tokens: list[str], start: int, end: int) -> tuple[int, int]:
    """Regel 1: Modifikatoren, Artikel und Satzzeichen an den Raendern abschneiden.

    Schneidet ausserdem eine angehaengte Klammer- oder Gedankenstrich-Gruppe ab, in der die
    Abkuerzung nachgestellt ist: ``E-Government-Gesetz Rheinland-Pfalz ( EGovGRP )`` und
    ``Onlinezugangsgesetz - OZG`` sind je ein Eigenname plus Beiwerk.
    """
    for i in range(start, end):
        if tokens[i] in {"(", "–", "—", "-", "/"} and i > start:
            end = i
            break
    while start < end and _ist_rand_muell(tokens[start]):
        start += 1
    while end > start and _ist_satzzeichen(tokens[end - 1]):
        end -= 1
    return start, end


def ist_eigenname(oberflaeche: str) -> str | None:
    """Regel 2: Traegt diese Oberflaeche einen Eigennamen, und welchen Typ?

    Gibt das Label zurueck oder ``None``, wenn der Span nach ANNOTATION.md keine Entitaet ist.
    """
    if oberflaeche in GATTUNG:
        return None
    if oberflaeche in LEX_LOC:
        return "LOC"
    if oberflaeche in LEX_ORG:
        return "ORG"
    if oberflaeche in LEX_PER:
        return "PER"
    klein = oberflaeche.lower()
    if any(teil in klein for teil in OTH_BESTANDTEILE):
        return "OTH"
    if any(ABKUERZUNG.search(tok) for tok in oberflaeche.split()):
        return "OTH"
    return None


def _zitat_kern(tokens: list[str], start: int, end: int) -> tuple[int, int]:
    """Regel 3: In einer Fundstelle steckt der Gesetzesname, nicht die Paragraphenangabe.

    ``§ 2 Absatz 1 OZG`` wird zu ``OZG``, ``§ 9 des deutschen Verwaltungsverfahrensgesetzes`` zu
    ``Verwaltungsverfahrensgesetzes``. ``Artikel 91c V`` traegt keinen Namen und faellt danach
    durch den Eigennamen-Test.
    """
    while start < end and (tokens[start] in ZITAT_ANFANG or _ist_rand_muell(tokens[start])):
        start += 1
    return start, end


def normalisiere_span(tokens: list[str], span: Span) -> Span | None:
    """Einen Span auf die Richtlinien ziehen, oder ``None``, wenn er keine Entitaet ist."""
    start, end = _trimme(tokens, span.start, span.end)
    if start >= end:
        return None
    if tokens[span.start] in ZITAT_ANFANG or tokens[start] in ZITAT_ANFANG:
        start, end = _zitat_kern(tokens, start, end)
        if start >= end:
            return None
    label = ist_eigenname(" ".join(tokens[start:end]))
    if label is None:
        return None
    return Span(start=start, end=end, label=label)


def ohne_ueberlappung(spans: list[Span]) -> list[Span]:
    """Nach dem Trimmen koennen Spans zusammenfallen; der laengere gewinnt, dann der fruehere."""
    gewaehlt: list[Span] = []
    for span in sorted(spans, key=lambda s: (-(s.end - s.start), s.start)):
        if all(span.end <= g.start or span.start >= g.end for g in gewaehlt):
            gewaehlt.append(span)
    return sorted(gewaehlt, key=lambda s: s.start)


def normalisiere_satz(satz: Sentence, protokoll: Protokoll | None = None) -> Sentence:
    """Alle Spans eines Satzes normalisieren und den Satz aufraeumen."""
    neu: list[Span] = []
    for span in satz.spans:
        alt = " ".join(satz.tokens[span.start : span.end])
        norm = normalisiere_span(satz.tokens, span)
        if norm is None:
            if protokoll is not None:
                protokoll.verworfen.append((alt, span.label))
            continue
        jetzt = " ".join(satz.tokens[norm.start : norm.end])
        if protokoll is not None:
            if jetzt == alt and norm.label == span.label:
                protokoll.behalten.append((alt, norm.label))
            else:
                protokoll.getrimmt.append((f"{alt} [{span.label}]", f"{jetzt} [{norm.label}]"))
        neu.append(norm)
    return Sentence(
        id=satz.id, tokens=satz.tokens, spans=ohne_ueberlappung(neu), source=satz.source
    )


def normalisiere(saetze: list[Sentence]) -> tuple[list[Sentence], Protokoll]:
    """Eine ganze Datei normalisieren und dabei protokollieren, was passiert ist."""
    protokoll = Protokoll(behalten=[], getrimmt=[], verworfen=[])
    return [normalisiere_satz(s, protokoll) for s in saetze], protokoll
