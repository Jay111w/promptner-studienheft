"""Zentrale Logging-Konfiguration.

Schreibt strukturiert auf Konsole und in eine rotierende Logdatei.
Wird einmalig beim App-Start aufgerufen.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_APP_DIRNAME = "Studienheft-Korrektor"


def _user_log_dir() -> Path:
    """Liefert ein garantiert beschreibbares Log-Verzeichnis pro Benutzer.

    Auf Windows unter ``%LOCALAPPDATA%``, sonst unter dem Home-Verzeichnis.
    Wichtig fuer die gebuendelte App, deren Arbeitsverzeichnis schreibgeschuetzt
    sein kann.
    """
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / _APP_DIRNAME / "logs"


def resolve_log_dir(log_dir: str) -> Path:
    """Bestimmt das tatsaechliche Log-Verzeichnis.

    Absolute Pfade werden unveraendert genutzt (z. B. in Tests); relative oder
    leere Angaben landen im Benutzer-Log-Verzeichnis.
    """
    if log_dir:
        candidate = Path(log_dir)
        if candidate.is_absolute():
            return candidate
    return _user_log_dir()


def setup_logging(level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """Initialisiert das Wurzel-Logging der Anwendung.

    Schlaegt das Anlegen der Logdatei fehl (z. B. fehlende Schreibrechte),
    laeuft die App trotzdem weiter und protokolliert nur auf der Konsole.

    Args:
        level: Log-Level als String (z. B. ``"INFO"``, ``"DEBUG"``).
        log_dir: Verzeichnis fuer die Logdateien (relativ -> Benutzerordner).

    Returns:
        Den konfigurierten Logger fuer das ``korrektor``-Paket.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger("korrektor")
    root.setLevel(numeric_level)
    root.handlers.clear()  # doppelte Handler bei Re-Init vermeiden
    root.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    try:
        log_path = resolve_log_dir(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path / "korrektor.log",
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError as exc:
        # Datei-Logging ist optional - niemals deswegen abstuerzen.
        root.warning("Datei-Logging deaktiviert (%s): %s", type(exc).__name__, exc)

    return root


def get_logger(name: str) -> logging.Logger:
    """Liefert einen Logger unterhalb des ``korrektor``-Namensraums."""
    return logging.getLogger(f"korrektor.{name}")
