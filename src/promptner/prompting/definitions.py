"""Modulare Definitionen je Datensatz (Ashok & Lipton 2023, Abschnitt 3: "Modular Definitions").

Die Definition beschreibt in natuerlicher Sprache, was als Entitaet gilt und was
nicht. Der Typname in Klammern ist derjenige, den das Modell in seiner Antwort
verwenden soll; ``TYPE_ALIASES`` bildet ihn (und uebliche Varianten) auf das Label ab.
"""

from __future__ import annotations

DEFINITIONS: dict[str, str] = {
    "conll2003": (
        "An entity is a person (person), an organisation (organisation) such as a company, "
        "institution, government body or sports team, a location (location) such as a city, "
        "country, region or river, or a miscellaneous named entity (miscellaneous) such as a "
        "nationality, an event, a product, a work of art or a language. Entities are proper "
        "names or nicknames as they appear in the text; a nationality or demonym like "
        "'German' counts as miscellaneous. Dates, times, numbers, amounts, job titles, "
        "common nouns, adjectives and verbs are not entities."
    ),
    "germeval14": (
        "Eine Entität ist eine Person (Person), eine Organisation (Organisation) wie ein "
        "Unternehmen, eine Behörde, eine Partei, ein Verein oder eine Institution, ein Ort (Ort) "
        "wie eine Stadt, ein Land, eine Region, ein Fluss oder ein Gebäude mit Eigennamen, oder "
        "ein sonstiger Eigenname (Sonstiges) wie ein Werk, ein Produkt, ein Ereignis, ein Gesetz "
        "oder eine Sprache. Entitäten sind Eigennamen, so wie sie im Text stehen. Ableitungen "
        "wie 'deutsche' oder 'Berliner' als Adjektiv sind keine Entitäten. Daten, Uhrzeiten, "
        "Zahlen, Berufsbezeichnungen, Gattungsbegriffe, Adjektive und Verben sind keine Entitäten."
    ),
    "studienheft": (
        "Eine Entität ist eine Person (Person), eine Organisation (Organisation) wie ein "
        "Unternehmen, eine Hochschule, eine Behörde oder ein Verband, ein Ort (Ort) wie eine "
        "Stadt, ein Land oder eine Region, oder ein sonstiger Eigenname (Sonstiges) wie ein "
        "Gesetz, ein Produkt, eine Norm, ein Werk oder ein Ereignis. Entitäten sind Eigennamen, "
        "so wie sie im Text stehen. Fachbegriffe, Gattungsbegriffe, Abkürzungen ohne "
        "Eigennamencharakter, Daten, Zahlen, Adjektive und Verben sind keine Entitäten."
    ),
}

QUESTION: dict[str, str] = {
    "conll2003": (
        "Given the paragraph below, identify a list of possible entities and for each entry "
        "explain why it either is or is not an entity:"
    ),
    "germeval14": (
        "Nenne für den folgenden Absatz eine Liste möglicher Entitäten und begründe für jeden "
        "Eintrag, warum er eine Entität ist oder nicht:"
    ),
    "studienheft": (
        "Nenne für den folgenden Absatz eine Liste möglicher Entitäten und begründe für jeden "
        "Eintrag, warum er eine Entität ist oder nicht:"
    ),
}

# Typname (wie vom Modell genannt, kleingeschrieben) -> Label des Datensatzes.
_EN = {
    "person": "PER",
    "people": "PER",
    "per": "PER",
    "organisation": "ORG",
    "organization": "ORG",
    "org": "ORG",
    "company": "ORG",
    "institution": "ORG",
    "team": "ORG",
    "location": "LOC",
    "loc": "LOC",
    "place": "LOC",
    "city": "LOC",
    "country": "LOC",
    "miscellaneous": "MISC",
    "misc": "MISC",
    "other": "MISC",
    "nationality": "MISC",
    "event": "MISC",
    "product": "MISC",
}
_DE = {
    "person": "PER",
    "personen": "PER",
    "per": "PER",
    "organisation": "ORG",
    "organization": "ORG",
    "org": "ORG",
    "unternehmen": "ORG",
    "firma": "ORG",
    "behörde": "ORG",
    "partei": "ORG",
    "verein": "ORG",
    "institution": "ORG",
    "ort": "LOC",
    "location": "LOC",
    "loc": "LOC",
    "stadt": "LOC",
    "land": "LOC",
    "region": "LOC",
    "sonstiges": "OTH",
    "sonstige": "OTH",
    "oth": "OTH",
    "other": "OTH",
    "misc": "OTH",
    "werk": "OTH",
    "produkt": "OTH",
    "ereignis": "OTH",
    "gesetz": "OTH",
}
TYPE_ALIASES: dict[str, dict[str, str]] = {"conll2003": _EN, "germeval14": _DE, "studienheft": _DE}


def resolve_type(dataset: str, type_name: str | None) -> str | None:
    """Bildet den vom Modell genannten Typnamen auf ein Label ab (``None`` = unbekannt)."""
    if not type_name:
        return None
    return TYPE_ALIASES[dataset].get(type_name.strip().strip("()").lower())
