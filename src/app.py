#!/usr/bin/env python3
"""
YourBrowser - Native Multi-Platform Privacy Browser
Entry point for the YourBrowser application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Ensure src module is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure Chromium sandbox flag is safely handled
if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from src.ui.dashboard_window import DashboardWindow
from src.ui.browser_window import YourBrowserWindow

def main():
    # Setup High DPI scaling and attributes
    QApplication.setApplicationName("YourBrowser")
    QApplication.setApplicationDisplayName("YourBrowser")
    QApplication.setDesktopFileName("yourbrowser.desktop")

    app = QApplication(sys.argv)

    # Set Application Icon
    icon_path = os.path.join(PROJECT_ROOT, "assets", "icons", "yourbrowser.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Parse initial URL from arguments if present
    initial_url = None
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            initial_url = arg
            break

    # Launch Profile Dashboard as primary entry point
    dashboard = DashboardWindow(initial_url=initial_url)
    dashboard.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
