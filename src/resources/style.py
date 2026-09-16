"""
YourBrowser UI Styling - Ultra-Modern Brave Obsidian Pro Theme
Designed for production-level desktop aesthetics with high-contrast accents and smooth micro-states.
"""

BRAVE_THEME_QSS = """
QMainWindow {
    background-color: #0A0C10;
    color: #F8FAFC;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #E2E8F0;
}

/* ========================================================== */
/* Top Tab Strip                                              */
/* ========================================================== */
QTabWidget::pane {
    border: none;
    background-color: #0A0C10;
}

QTabBar {
    background-color: #0B0E14;
    qproperty-drawBase: 0;
    border: none;
    padding-top: 6px;
    padding-left: 6px;
}

QTabBar::tab {
    background-color: #151922;
    color: #8E9BAE;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    min-width: 140px;
    max-width: 240px;
    border: 1px solid #1E2533;
    border-bottom: none;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222938, stop:1 #1A1F2C);
    color: #FFFFFF;
    font-weight: 600;
    border-top: 2px solid #FF5500;
    border-left: 1px solid #2D374D;
    border-right: 1px solid #2D374D;
}

QTabBar::tab:hover:!selected {
    background-color: #1B212D;
    color: #CBD5E1;
    border-top: 1px solid #334155;
}

/* Tab Close Button */
QTabBar::close-button {
    subcontrol-position: right;
    margin-right: 4px;
    border-radius: 4px;
    padding: 2px;
}

QTabBar::close-button:hover {
    background-color: rgba(239, 68, 68, 0.2);
}

/* ========================================================== */
/* Main Navigation Toolbar                                    */
/* ========================================================== */
#nav_toolbar {
    background-color: #1A1F2C;
    border-bottom: 1px solid #252D3E;
    padding: 6px 12px;
}

/* Action & Nav Buttons */
QPushButton.nav-btn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 8px;
    color: #94A3B8;
}

QPushButton.nav-btn:hover {
    background-color: #262E40;
    border: 1px solid #364259;
    color: #FFFFFF;
}

QPushButton.nav-btn:pressed {
    background-color: #1C2230;
}

QPushButton#new_tab_btn {
    background-color: #151922;
    border: 1px solid #252D3E;
    border-radius: 8px;
    padding: 5px 10px;
    color: #94A3B8;
}

QPushButton#new_tab_btn:hover {
    background-color: #252D3E;
    color: #FFFFFF;
    border: 1px solid #38BDF8;
}

/* ========================================================== */
/* Omnibox / Search & Address Bar                             */
/* ========================================================== */
QLineEdit#omnibox {
    background-color: #0E121A;
    border: 1px solid #283144;
    border-radius: 19px;
    padding: 7px 18px;
    color: #F8FAFC;
    font-size: 13px;
    selection-background-color: #FF5500;
}

QLineEdit#omnibox:hover {
    border: 1px solid #38455E;
    background-color: #111520;
}

QLineEdit#omnibox:focus {
    border: 1px solid #FF5500;
    background-color: #121724;
}

/* SSL Padlock Icon Inside/Beside Omnibox */
QLabel#ssl_badge {
    color: #10B981;
    font-weight: bold;
    padding-right: 4px;
}

/* ========================================================== */
/* Brave Shields Badge Button                                 */
/* ========================================================== */
QPushButton#shield_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    border-radius: 15px;
    padding: 6px 14px;
    border: 1px solid rgba(255, 255, 255, 0.15);
}

QPushButton#shield_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6A1F, stop:1 #FF4267);
}

QPushButton#shield_btn:pressed {
    background: #E04000;
}

/* ========================================================== */
/* Tab Lock Button (Cyber Shield Style)                       */
/* ========================================================== */
QPushButton#lock_btn {
    background-color: #132230;
    color: #38BDF8;
    font-weight: 600;
    font-size: 12px;
    border-radius: 15px;
    padding: 6px 14px;
    border: 1px solid #0284C7;
}

QPushButton#lock_btn:hover {
    background-color: #38BDF8;
    color: #0A0C10;
    border: 1px solid #38BDF8;
}

QPushButton#lock_btn:pressed {
    background-color: #0284C7;
    color: #FFFFFF;
}

/* ========================================================== */
/* Minimalist Status Bar                                      */
/* ========================================================== */
QStatusBar {
    background-color: #0B0E14;
    color: #64748B;
    border-top: 1px solid #1E2533;
    padding: 3px 8px;
    font-size: 11px;
}
"""
