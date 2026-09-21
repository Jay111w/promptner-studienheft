"""Unit-Tests fuer Definitionen und Typ-Aliases."""

import pytest

from promptner.data.loaders import DATASETS
from promptner.prompting.definitions import DEFINITIONS, QUESTION, resolve_type


@pytest.mark.unit
@pytest.mark.parametrize("dataset", ["conll2003", "germeval14", "studienheft"])
def test_definition_and_question_exist(dataset):
    assert len(DEFINITIONS[dataset]) > 100
    assert dataset in QUESTION


@pytest.mark.unit
def test_definition_mentions_every_type_name():
    assert all(
        t in DEFINITIONS["conll2003"]
        for t in ("person", "organisation", "location", "miscellaneous")
    )
    assert all(
        t in DEFINITIONS["germeval14"] for t in ("Person", "Organisation", "Ort", "Sonstiges")
    )


@pytest.mark.unit
def test_resolve_type_aliases():
    assert resolve_type("conll2003", "person") == "PER"
    assert resolve_type("conll2003", "Organization") == "ORG"
    assert resolve_type("conll2003", "misc") == "MISC"
    assert resolve_type("germeval14", "Ort") == "LOC"
    assert resolve_type("germeval14", "sonstiges") == "OTH"
    assert resolve_type("germeval14", "Unternehmen") == "ORG"
    assert resolve_type("conll2003", "date") is None


@pytest.mark.unit
def test_resolved_labels_are_valid_for_dataset():
    from promptner.prompting.definitions import TYPE_ALIASES

    for ds, labels in DATASETS.items():
        assert set(TYPE_ALIASES[ds].values()) <= set(labels)
