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

# Determine dark mode status for Chromium web rendering
from src.core.browser_data import is_system_dark_mode, SettingsManager

try:
    _settings = SettingsManager()
    _web_dark_pref = _settings.get("web_dark_mode", "auto")
    _should_dark = False
    if _web_dark_pref == "dark":
        _should_dark = True
    elif _web_dark_pref == "light":
        _should_dark = False
    else:
        _theme_mode = _settings.get("theme_mode", "brave_dark")
        _should_dark = (_theme_mode != "light") or is_system_dark_mode()

    _flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox")
    if _should_dark and "--force-dark-mode" not in _flags:
        _flags = f"{_flags} --force-dark-mode"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = _flags
except Exception:
    if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

# Ensure GTK platform theme is integrated if running in a GTK/GNOME/Cinnamon environment
if sys.platform.startswith("linux") and "QT_QPA_PLATFORMTHEME" not in os.environ:
    os.environ["QT_QPA_PLATFORMTHEME"] = "gtk3"

from PyQt6.QtCore import Qt, QCoreApplication
# Must be set before QApplication is instantiated for QtWebEngine
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

from PyQt6.QtWebEngineWidgets import QWebEngineView
from src.ui.dashboard_window import DashboardWindow
from src.ui.browser_window import YourBrowserWindow

def main():
    # Setup High DPI scaling and attributes
    QApplication.setApplicationName("YourBrowser")
    QApplication.setApplicationDisplayName("YourBrowser")
    QApplication.setDesktopFileName("yourbrowser.desktop")

    app = QApplication(sys.argv)

    # Set Application Icon
    from src.resources.icons import get_app_icon
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

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
