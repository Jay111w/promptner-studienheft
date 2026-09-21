"""Handgeschriebener Few-Shot-Pool je Datensatz.

Jedes Beispiel folgt Figure 1 des Papers: ein Absatz und eine Kandidatenliste mit
True- und False-Entscheidungen plus Begruendung. Die False-Kandidaten sind der
Kern der "Cand"-Komponente. Auswahl von k Beispielen erfolgt deterministisch je Seed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from promptner.domain import Candidate


@dataclass(frozen=True)
class Example:
    tokens: tuple[str, ...]
    candidates: tuple[Candidate, ...]


def _ex(text: str, *cands: tuple) -> Example:
    return Example(
        tokens=tuple(text.split(" ")),
        candidates=tuple(
            Candidate(text=t, is_entity=e, explanation=x, type_name=ty) for t, e, x, ty in cands
        ),
    )


_CONLL = [
    _ex(
        "EU rejects German call to boycott British lamb .",
        ("EU", True, "as the European Union is a political organisation", "organisation"),
        ("German", True, "as it is a nationality, which counts as miscellaneous", "miscellaneous"),
        ("British", True, "as it is a nationality, which counts as miscellaneous", "miscellaneous"),
        ("lamb", False, "as it is a common noun for a product, not a named entity", None),
    ),
    _ex(
        "Peter Blackburn reported from Brussels on Thursday .",
        ("Peter Blackburn", True, "as it is the name of a person", "person"),
        ("Brussels", True, "as it is a city", "location"),
        ("Thursday", False, "as days and dates are not entities", None),
    ),
    _ex(
        "West Indian all-rounder Phil Simmons took four for 38 as Leicestershire beat Somerset .",
        (
            "West Indian",
            True,
            "as it is a nationality or demonym, which counts as miscellaneous",
            "miscellaneous",
        ),
        ("Phil Simmons", True, "as it is the name of a cricketer", "person"),
        (
            "Leicestershire",
            True,
            "as here it names the county cricket club, a sports team",
            "organisation",
        ),
        (
            "Somerset",
            True,
            "as here it names the county cricket club, a sports team",
            "organisation",
        ),
        ("all-rounder", False, "as it is a role description, not a name", None),
        ("38", False, "as numbers are not entities", None),
    ),
    _ex(
        "The Bank of Japan said the yen would stay stable against the dollar .",
        ("Bank of Japan", True, "as it is a central bank, an institution", "organisation"),
        (
            "Japan",
            False,
            "as here it is part of the longer organisation name and not a separate mention",
            None,
        ),
        ("yen", False, "as a currency name is a common noun here, not a named entity", None),
        ("dollar", False, "as a currency name is a common noun here, not a named entity", None),
    ),
    _ex(
        "Microsoft Corp released Windows 95 in the United States last August .",
        ("Microsoft Corp", True, "as it is a company", "organisation"),
        (
            "Windows 95",
            True,
            "as it is a named product, which counts as miscellaneous",
            "miscellaneous",
        ),
        ("United States", True, "as it is a country", "location"),
        ("last August", False, "as dates and months are not entities", None),
    ),
    _ex(
        "Prime Minister John Major met the French president in Paris .",
        ("Prime Minister", False, "as a job title is not an entity", None),
        ("John Major", True, "as it is the name of a person", "person"),
        ("French", True, "as it is a nationality, which counts as miscellaneous", "miscellaneous"),
        ("president", False, "as it is a job title, not a name", None),
        ("Paris", True, "as it is a city", "location"),
    ),
    _ex(
        "The Rhine flooded parts of Cologne after heavy rain in Germany .",
        ("Rhine", True, "as it is a river, a geographic location", "location"),
        ("Cologne", True, "as it is a city", "location"),
        ("heavy rain", False, "as it is a weather description, not a name", None),
        ("Germany", True, "as it is a country", "location"),
    ),
    _ex(
        "Real Madrid signed striker Davor Suker from Sevilla for 4 million dollars .",
        ("Real Madrid", True, "as it is a football club, a sports team", "organisation"),
        ("striker", False, "as it is a position, not a name", None),
        ("Davor Suker", True, "as it is the name of a footballer", "person"),
        (
            "Sevilla",
            True,
            "as here it names the football club that sold the player",
            "organisation",
        ),
        ("4 million dollars", False, "as amounts of money are not entities", None),
    ),
    _ex(
        "The 1996 Olympic Games in Atlanta opened with a speech by Bill Clinton .",
        (
            "1996 Olympic Games",
            True,
            "as it is a named event, which counts as miscellaneous",
            "miscellaneous",
        ),
        ("Atlanta", True, "as it is a city", "location"),
        ("speech", False, "as it is a common noun", None),
        ("Bill Clinton", True, "as it is the name of a person", "person"),
    ),
    _ex(
        "Shares of Siemens AG rose 2 percent on the Frankfurt stock exchange .",
        ("Siemens AG", True, "as it is a company", "organisation"),
        ("2 percent", False, "as percentages are not entities", None),
        ("Frankfurt", True, "as it is a city, even when used to describe the exchange", "location"),
        ("stock exchange", False, "as it is a common noun without a proper name here", None),
    ),
    _ex(
        "Reuters correspondent Mark Trevelyan writes from Moscow about the Chechen conflict .",
        ("Reuters", True, "as it is a news agency, a company", "organisation"),
        ("correspondent", False, "as it is a job title", None),
        ("Mark Trevelyan", True, "as it is the name of a person", "person"),
        ("Moscow", True, "as it is a city", "location"),
        ("Chechen", True, "as it is a demonym, which counts as miscellaneous", "miscellaneous"),
        ("conflict", False, "as it is a common noun", None),
    ),
    _ex(
        "Nobel laureate Toni Morrison spoke at Princeton University about English literature .",
        (
            "Nobel laureate",
            False,
            "as it is a title or description, not the name of a person",
            None,
        ),
        ("Toni Morrison", True, "as it is the name of a person", "person"),
        ("Princeton University", True, "as it is a university, an institution", "organisation"),
        ("English", True, "as it is a language, which counts as miscellaneous", "miscellaneous"),
        ("literature", False, "as it is a common noun", None),
    ),
]

_GERMEVAL = [
    _ex(
        "Firmengründer Wolf Peter Bree arbeitete Anfang der siebziger Jahre in Berlin .",
        ("Firmengründer", False, "da es eine Berufsbezeichnung ist, kein Name", None),
        ("Wolf Peter Bree", True, "da es der Name einer Person ist", "Person"),
        ("Anfang der siebziger Jahre", False, "da Zeitangaben keine Entitäten sind", None),
        ("Berlin", True, "da es eine Stadt ist", "Ort"),
    ),
    _ex(
        "Die Deutsche Bahn will 2015 neue ICE-Züge auf der Strecke München – Hamburg einsetzen .",
        ("Deutsche Bahn", True, "da es ein Unternehmen ist", "Organisation"),
        ("2015", False, "da Jahreszahlen keine Entitäten sind", None),
        ("ICE-Züge", False, "da es ein Gattungsbegriff für einen Zugtyp ist, kein Eigenname", None),
        ("München", True, "da es eine Stadt ist", "Ort"),
        ("Hamburg", True, "da es eine Stadt ist", "Ort"),
    ),
    _ex(
        "Angela Merkel traf den französischen Präsidenten in Paris .",
        ("Angela Merkel", True, "da es der Name einer Person ist", "Person"),
        ("französischen", False, "da es ein abgeleitetes Adjektiv ist, keine Entität", None),
        ("Präsidenten", False, "da es eine Amtsbezeichnung ist, kein Name", None),
        ("Paris", True, "da es eine Stadt ist", "Ort"),
    ),
    _ex(
        "Der Roman Die Blechtrommel von Günter Grass erschien 1959 im Luchterhand Verlag .",
        ("Roman", False, "da es ein Gattungsbegriff ist", None),
        ("Die Blechtrommel", True, "da es der Titel eines Werks ist", "Sonstiges"),
        ("Günter Grass", True, "da es der Name einer Person ist", "Person"),
        ("1959", False, "da Jahreszahlen keine Entitäten sind", None),
        ("Luchterhand Verlag", True, "da es ein Unternehmen ist", "Organisation"),
    ),
    _ex(
        "Der FC Bayern München gewann das Finale der Champions League gegen Borussia Dortmund .",
        ("FC Bayern München", True, "da es ein Sportverein ist", "Organisation"),
        ("Finale", False, "da es ein Gattungsbegriff ist", None),
        (
            "Champions League",
            True,
            "da es ein benannter Wettbewerb, also ein Ereignis ist",
            "Sonstiges",
        ),
        ("Borussia Dortmund", True, "da es ein Sportverein ist", "Organisation"),
    ),
    _ex(
        "Das Bundesverfassungsgericht in Karlsruhe prüft das Gesetz zur Vorratsdatenspeicherung .",
        ("Bundesverfassungsgericht", True, "da es eine Institution ist", "Organisation"),
        ("Karlsruhe", True, "da es eine Stadt ist", "Ort"),
        ("Gesetz zur Vorratsdatenspeicherung", True, "da es ein benanntes Gesetz ist", "Sonstiges"),
        ("prüft", False, "da Verben keine Entitäten sind", None),
    ),
    _ex(
        "Die Berliner Philharmoniker spielten unter Simon Rattle die Neunte Sinfonie von Beethoven .",
        (
            "Berliner Philharmoniker",
            True,
            "da es ein Orchester, also eine Organisation ist",
            "Organisation",
        ),
        ("Simon Rattle", True, "da es der Name einer Person ist", "Person"),
        ("Neunte Sinfonie", True, "da es der Titel eines Werks ist", "Sonstiges"),
        ("Beethoven", True, "da es der Name einer Person ist", "Person"),
        ("spielten", False, "da Verben keine Entitäten sind", None),
    ),
    _ex(
        "Der Rhein entspringt in den Schweizer Alpen und mündet in die Nordsee .",
        ("Rhein", True, "da es ein Fluss ist", "Ort"),
        ("Schweizer", False, "da es ein abgeleitetes Adjektiv ist, keine Entität", None),
        ("Alpen", True, "da es ein Gebirge, also ein Ort ist", "Ort"),
        ("Nordsee", True, "da es ein Meer, also ein Ort ist", "Ort"),
    ),
    _ex(
        "Der Konzern Siemens verlegte seine Zentrale nach München und entließ 3000 Mitarbeiter .",
        ("Konzern", False, "da es ein Gattungsbegriff ist", None),
        ("Siemens", True, "da es ein Unternehmen ist", "Organisation"),
        ("Zentrale", False, "da es ein Gattungsbegriff ist", None),
        ("München", True, "da es eine Stadt ist", "Ort"),
        ("3000 Mitarbeiter", False, "da Zahlen und Gattungsbegriffe keine Entitäten sind", None),
    ),
    _ex(
        "Microsoft stellte Windows 10 auf der CeBIT in Hannover vor .",
        ("Microsoft", True, "da es ein Unternehmen ist", "Organisation"),
        ("Windows 10", True, "da es ein benanntes Produkt ist", "Sonstiges"),
        ("CeBIT", True, "da es eine benannte Messe, also ein Ereignis ist", "Sonstiges"),
        ("Hannover", True, "da es eine Stadt ist", "Ort"),
        ("stellte", False, "da Verben keine Entitäten sind", None),
    ),
    _ex(
        "Die SPD und die Grünen einigten sich im Landtag von Niedersachsen auf einen Koalitionsvertrag .",
        ("SPD", True, "da es eine Partei ist", "Organisation"),
        ("Grünen", True, "da es hier die Partei bezeichnet", "Organisation"),
        (
            "Landtag",
            False,
            "da es hier als Gattungsbegriff ohne vollständigen Eigennamen steht",
            None,
        ),
        ("Niedersachsen", True, "da es ein Bundesland, also ein Ort ist", "Ort"),
        ("Koalitionsvertrag", False, "da es ein Gattungsbegriff ist", None),
    ),
    _ex(
        "Der Physiker Albert Einstein lehrte an der Universität Zürich , bevor er in die USA emigrierte .",
        ("Physiker", False, "da es eine Berufsbezeichnung ist", None),
        ("Albert Einstein", True, "da es der Name einer Person ist", "Person"),
        (
            "Universität Zürich",
            True,
            "da es eine Hochschule, also eine Institution ist",
            "Organisation",
        ),
        ("USA", True, "da es ein Land ist", "Ort"),
    ),
]

EXAMPLE_POOL: dict[str, list[Example]] = {
    "conll2003": _CONLL,
    "germeval14": _GERMEVAL,
    "studienheft": _GERMEVAL,  # gleiche Sprache und Labels; Domaenen-Beispiele folgen mit dem Sample
}


def select_examples(dataset: str, k: int, seed: int) -> list[Example]:
    """Waehlt k Beispiele deterministisch je Seed (ohne Zuruecklegen)."""
    if k == 0:
        return []
    pool = EXAMPLE_POOL[dataset]
    rng = random.Random(seed)
    return rng.sample(pool, k=min(k, len(pool)))
