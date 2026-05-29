"""OPM OPM Acquisition — Application entry point.

Launches the PyQt6 application with the main window, dark theme,
and structured logging.
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles import APP_STYLESHEET


def _setup_logging() -> None:
    """Configure structured logging to console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """Create and run the OPM acquisition application."""
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting OPM OPM Acquisition…")

    app = QApplication(sys.argv)
    app.setApplicationName("OPM OPM Acquisition")
    app.setOrganizationName("OPM")
    app.setOrganizationDomain("opm.local")

    # Apply the premium dark theme.
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.showMaximized()

    logger.info("Application ready.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
