"""Unit-Tests fuer den Cache-Export (Nachspielen ohne API-Key)."""

import sys

import pytest

sys.path.insert(0, "scripts")

from export_cache import backup_sqlite  # noqa: E402

from promptner.llm.cache import ResponseCache  # noqa: E402


@pytest.mark.unit
def test_backup_copies_every_entry(tmp_path):
    src = tmp_path / "live"
    cache = ResponseCache(src)
    for i in range(5):
        cache.put(f"k{i}", f"antwort {i}")
    assert len(cache) == 5

    out = tmp_path / "replay"
    size = backup_sqlite(src / "cache.db", out / "cache.db")
    assert size > 0

    copy = ResponseCache(out)
    assert len(copy) == 5
    assert copy.get("k3") == "antwort 3"
    copy.close()
    cache.close()


@pytest.mark.unit
def test_backup_works_while_the_cache_is_open_and_unflushed(tmp_path):
    """Der eigentliche Zweck: waehrend eines Laufs stehen neue Eintraege noch im WAL.

    Ein blosses Kopieren der .db-Datei wuerde sie verlieren.
    """
    src = tmp_path / "live"
    cache = ResponseCache(src)
    cache.put("frisch", "noch nicht ausgecheckpointet")

    out = tmp_path / "replay"
    backup_sqlite(src / "cache.db", out / "cache.db")

    copy = ResponseCache(out)
    assert copy.get("frisch") == "noch nicht ausgecheckpointet"
    copy.close()
    cache.close()


@pytest.mark.unit
def test_backup_rejects_missing_database(tmp_path):
    import typer

    with pytest.raises(typer.BadParameter):
        backup_sqlite(tmp_path / "gibtsnicht" / "cache.db", tmp_path / "out" / "cache.db")
