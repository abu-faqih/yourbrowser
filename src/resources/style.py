"""
YourBrowser UI Styling - Ultra-Modern Brave Obsidian Pro Theme
Redesigned with top-level tabs, integrated capsule omnibox, and seamless layout.
"""

BRAVE_THEME_QSS = """
QMainWindow {
    background-color: #0B0E14;
    color: #F8FAFC;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #E2E8F0;
}

/* ========================================================== */
/* Top Level Tab Strip Bar                                    */
/* ========================================================== */
#top_tab_strip {
    background-color: #0B0E14;
    border-bottom: 1px solid #1C202C;
    padding-top: 4px;
    padding-left: 8px;
    padding-right: 8px;
}

QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
    border: none;
}

QTabBar::tab {
    background-color: #12151D;
    color: #8E9BAE;
    padding: 7px 16px;
    margin-right: 3px;
    border-top-left-radius: 9px;
    border-top-right-radius: 9px;
    min-width: 140px;
    max-width: 220px;
    border: 1px solid #1B212D;
    border-bottom: none;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #1C202C;
    color: #FFFFFF;
    font-weight: 600;
    border-top: 2px solid #FF5500;
    border-left: 1px solid #283042;
    border-right: 1px solid #283042;
}

QTabBar::tab:hover:!selected {
    background-color: #161A24;
    color: #CBD5E1;
    border-top: 1px solid #2A3346;
}

QTabBar::close-button {
    subcontrol-position: right;
    margin-right: 4px;
    border-radius: 8px;
    padding: 2px;
}

QTabBar::close-button:hover {
    background-color: rgba(239, 68, 68, 0.25);
}

/* New Tab Button next to tabs */
QPushButton#new_tab_btn {
    background-color: #12151D;
    border: 1px solid #1B212D;
    border-radius: 8px;
    padding: 5px 8px;
    color: #94A3B8;
    margin-left: 4px;
    margin-bottom: 2px;
}

QPushButton#new_tab_btn:hover {
    background-color: #1E2535;
    color: #FFFFFF;
    border: 1px solid #38BDF8;
}

/* ========================================================== */
/* Navigation Toolbar (Seamless directly below tab bar)      */
/* ========================================================== */
#nav_toolbar {
    background-color: #1C202C;
    border-bottom: 1px solid #283042;
    padding: 6px 12px;
}

/* Navigation action buttons */
QPushButton.nav-btn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 8px;
    color: #94A3B8;
}

QPushButton.nav-btn:hover {
    background-color: #272F42;
    border: 1px solid #37425B;
    color: #FFFFFF;
}

QPushButton.nav-btn:pressed {
    background-color: #1A1F2B;
}

/* ========================================================== */
/* True Pill Omnibox Frame (Fully Rounded Ends)              */
/* ========================================================== */
#omnibox_capsule {
    background-color: #0E121A;
    border: 1px solid #2B3347;
    border-radius: 19px;
    min-height: 36px;
    max-height: 38px;
    padding-left: 14px;
    padding-right: 12px;
}

#omnibox_capsule:hover {
    border: 1px solid #3F4B66;
    background-color: #111522;
}

QLineEdit#omnibox_input {
    background-color: transparent;
    border: none;
    padding: 2px 8px;
    color: #F8FAFC;
    font-size: 13.5px;
    selection-background-color: #FF5500;
}

QLineEdit#omnibox_input:focus {
    outline: none;
}

QLabel#ssl_icon_lbl {
    color: #10B981;
    font-size: 13px;
    margin-right: 2px;
}

QPushButton#bookmark_btn {
    background-color: transparent;
    border: none;
    border-radius: 12px;
    padding: 5px;
    color: #64748B;
}

QPushButton#bookmark_btn:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #FBBF24;
}


/* ========================================================== */
/* Brave Shields Pill Badge                                   */
/* ========================================================== */
QPushButton#shield_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    border-radius: 15px;
    padding: 6px 14px;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

QPushButton#shield_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6A1F, stop:1 #FF4267);
}

QPushButton#shield_btn:pressed {
    background: #E04000;
}

/* ========================================================== */
/* Tab Lock Button (Cyber Shield Pill)                        */
/* ========================================================== */
QPushButton#lock_btn {
    background-color: #11202E;
    color: #38BDF8;
    font-weight: 600;
    font-size: 12px;
    border-radius: 15px;
    padding: 6px 14px;
    border: 1px solid #0284C7;
}

QPushButton#lock_btn:hover {
    background-color: #38BDF8;
    color: #0A0D14;
    border: 1px solid #38BDF8;
}

QPushButton#lock_btn:pressed {
    background-color: #0284C7;
    color: #FFFFFF;
}

/* ========================================================== */
/* Floating Link Hover Tooltip (Modern overlay)               */
/* ========================================================== */
QLabel#floating_link_tooltip {
    background-color: #1E2535;
    color: #94A3B8;
    border: 1px solid #2B354C;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
}

/* ========================================================== */
/* Modern Dark Context Menu (Tab Right-Click Menu)           */
/* ========================================================== */
QMenu {
    background-color: #161A24;
    border: 1px solid #293448;
    border-radius: 12px;
    padding: 6px;
    color: #F1F5F9;
    font-size: 13px;
}

QMenu::item {
    padding: 8px 24px 8px 14px;
    border-radius: 8px;
    background-color: transparent;
}

QMenu::item:selected {
    background-color: #242D3E;
    color: #38BDF8;
}

QMenu::item:disabled {
    color: #4B5563;
}

QMenu::separator {
    height: 1px;
    background-color: #232B3B;
    margin: 5px 6px;
}

QMenu::icon {
    padding-left: 6px;
}

/* ========================================================== */
/* Bookmarks Bar                                              */
/* ========================================================== */
#bookmarks_bar {
    background-color: #121620;
    border-bottom: 1px solid #1C2333;
    min-height: 30px;
    max-height: 32px;
    padding: 2px 10px;
}

QPushButton.bookmark-bar-item {
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 12px;
    text-align: left;
}

QPushButton.bookmark-bar-item:hover {
    background-color: #1E2535;
    color: #F8FAFC;
    border: 1px solid #2B354C;
}

/* ========================================================== */
/* Find In Page Floating Bar                                  */
/* ========================================================== */
#find_bar {
    background-color: #161A24;
    border: 1px solid #293448;
    border-radius: 10px;
    padding: 4px 8px;
}

#find_input {
    background-color: #0E121A;
    border: 1px solid #2B3347;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 4px 8px;
    font-size: 12px;
    min-width: 180px;
}

#find_input:focus {
    border: 1px solid #38BDF8;
}

#find_match_lbl {
    color: #94A3B8;
    font-size: 12px;
    padding: 0 4px;
}

/* ========================================================== */
/* Zoom Indicator Badge in Omnibox                            */
/* ========================================================== */
QLabel#zoom_badge {
    background-color: #1E2535;
    color: #38BDF8;
    border: 1px solid #2B354C;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* ========================================================== */
/* Modern Dark Dialogs                                        */
/* ========================================================== */
QDialog {
    background-color: #0F131C;
    color: #F8FAFC;
}

QListWidget {
    background-color: #121620;
    border: 1px solid #212838;
    border-radius: 8px;
    color: #E2E8F0;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:selected {
    background-color: #242D3E;
    color: #38BDF8;
}

QListWidget::item:hover:!selected {
    background-color: #171D2B;
}

QLineEdit.dialog-search {
    background-color: #141924;
    border: 1px solid #263044;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 7px 12px;
    font-size: 13px;
}

QLineEdit.dialog-search:focus {
    border: 1px solid #FF5500;
}

QPushButton.dialog-btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54);
    color: #FFFFFF;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}

QPushButton.dialog-btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6A1F, stop:1 #FF4267);
}

QPushButton.dialog-btn-secondary {
    background-color: #1E2535;
    color: #CBD5E1;
    border: 1px solid #2B354C;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton.dialog-btn-secondary:hover {
    background-color: #262F44;
    color: #FFFFFF;
}

QPushButton.dialog-btn-danger {
    background-color: #7F1D1D;
    color: #FECACA;
    border: 1px solid #DC2626;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton.dialog-btn-danger:hover {
    background-color: #991B1B;
}
"""


