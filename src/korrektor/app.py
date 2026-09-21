"""Einstiegspunkt der Anwendung.

In dieser Aufbauphase fuehrt der Start einen Selbsttest durch und meldet
die vier zentralen Statuswerte. Die grafische Oberflaeche (PySide6) wird in
einer spaeteren Phase ergaenzt und hier eingehaengt.
"""

from __future__ import annotations

import sys

from korrektor import __version__
from korrektor.config import get_logger, get_settings, setup_logging


def run_self_check() -> dict[str, bool]:
    """Prueft die Grundvoraussetzungen und liefert die Statuswerte.

    Returns:
        Mapping der vier Statusindikatoren auf ihren Zustand.
    """
    settings = get_settings()
    return {
        "app_running": True,
        "api_configured": settings.has_api_key,
        "analysis_active": False,
        "has_errors": False,
    }


def _format_status(status: dict[str, bool]) -> str:
    def mark(ok: bool) -> str:
        return "OK" if ok else "--"

    return (
        f"  App laeuft:        {mark(status['app_running'])}\n"
        f"  OpenAI verbunden:  {mark(status['api_configured'])}\n"
        f"  Analyse aktiv:     {mark(status['analysis_active'])}\n"
        f"  Fehler:            {'JA' if status['has_errors'] else 'nein'}"
    )


def _ping(log) -> int:
    """Prueft die OpenAI-Verbindung mit dem konfigurierten Key."""
    from korrektor.errors import KorrektorError
    from korrektor.services.ai.openai_client import OpenAiClient

    try:
        OpenAiClient().verify_connection()
    except KorrektorError as exc:
        log.error("OpenAI-Verbindung fehlgeschlagen: %s", exc.code.value)
        print(f"\nOpenAI-Verbindung FEHLGESCHLAGEN: [{exc.code.value}] {exc.message}")
        return 1
    print("\nOpenAI-Verbindung OK.")
    log.info("OpenAI-Verbindung erfolgreich geprueft.")
    return 0


def launch_gui() -> int:
    """Startet die grafische Oberflaeche (PySide6).

    Returns:
        Exit-Code der Qt-Ereignisschleife.
    """
    from PySide6.QtWidgets import QApplication

    from korrektor.ui import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    """Startet die Anwendung.

    Mit ``--check`` wird nur ein Selbsttest ausgefuehrt (ohne GUI), andernfalls
    startet die grafische Oberflaeche.

    Returns:
        Exit-Code (0 = OK).
    """
    argv = argv or []
    settings = get_settings()
    setup_logging(level=settings.log_level, log_dir=settings.log_dir)
    log = get_logger("app")
    log.info("Studienheft-Korrektor v%s startet ...", __version__)

    status = run_self_check()
    print(f"Studienheft-Korrektor v{__version__}")
    print(_format_status(status))
    if not status["api_configured"]:
        log.warning("Kein OpenAI-API-Key gefunden. Bitte .env aus .env.example erstellen.")
        print("\nHinweis: Kein API-Key gesetzt. .env aus .env.example anlegen.")

    if "--ping" in argv:
        return _ping(log)

    if "--check" in argv:
        log.info("Selbsttest abgeschlossen (--check).")
        return 0

    log.info("Starte grafische Oberflaeche ...")
    return launch_gui()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
