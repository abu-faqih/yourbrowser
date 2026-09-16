"""
YourBrowser UI Styling - Brave Obsidian Dark Theme
"""

BRAVE_THEME_QSS = """
QMainWindow {
    background-color: #0F1115;
    color: #F0F2F5;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #E2E8F0;
}

/* Tab Bar */
QTabBar {
    background-color: #0B0D10;
    qproperty-drawBase: 0;
    border: none;
}

QTabBar::tab {
    background-color: #161920;
    color: #94A3B8;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 140px;
    max-width: 220px;
    border: 1px solid #1E232F;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #1E222D;
    color: #FFFFFF;
    font-weight: bold;
    border-top: 2px solid #FF5500;
}

QTabBar::tab:hover:!selected {
    background-color: #1A1E29;
    color: #CBD5E1;
}

QTabBar::close-button {
    image: none;
    subcontrol-position: right;
    margin-right: 2px;
}

/* Navigation Toolbar */
#nav_toolbar {
    background-color: #1E222D;
    border-bottom: 1px solid #2D3344;
    padding: 4px 8px;
}

/* Nav Buttons */
QPushButton.nav-btn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px;
    color: #94A3B8;
    font-weight: bold;
}

QPushButton.nav-btn:hover {
    background-color: #2D3344;
    color: #FFFFFF;
}

QPushButton.nav-btn:pressed {
    background-color: #383F54;
}

/* Omnibox / Address Bar */
QLineEdit#omnibox {
    background-color: #0F1115;
    border: 1px solid #2D3344;
    border-radius: 18px;
    padding: 6px 14px;
    color: #F8FAFC;
    selection-background-color: #FF5500;
}

QLineEdit#omnibox:focus {
    border: 1px solid #FF5500;
    background-color: #12151B;
}

/* Brave Shield Button */
QPushButton#shield_btn {
    background-color: #FF5500;
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 14px;
    padding: 4px 10px;
    border: none;
}

QPushButton#shield_btn:hover {
    background-color: #FF6E26;
}

/* Tab Lock Button */
QPushButton#lock_btn {
    background-color: #2A2F3D;
    color: #38BDF8;
    font-weight: bold;
    border-radius: 14px;
    padding: 4px 10px;
    border: 1px solid #38BDF8;
}

QPushButton#lock_btn:hover {
    background-color: #38BDF8;
    color: #0F1115;
}

/* Status Bar */
QStatusBar {
    background-color: #0B0D10;
    color: #64748B;
    border-top: 1px solid #1E232F;
}
"""
