"""
YourBrowser UI Styling - Ultra-Modern Brave Obsidian Pro Theme with Design System Tokens
Redesigned with top-level tabs, integrated capsule omnibox, pill buttons, and vibrant gradients.
"""

from src.resources.design_system import Colors, Gradients, Radii, Typography

BRAVE_THEME_QSS = f"""
QMainWindow {{
    background-color: {Colors.BG_CANVAS};
    color: {Colors.TEXT_PRIMARY};
}}

/* Specific UI components styling - Do NOT use generic QWidget to prevent leaking into QWebEngineView DOM */
QMainWindow, QDialog, QMenu, QTabBar, QLabel, QLineEdit, QPushButton, QListWidget, QGroupBox, QComboBox, QProgressBar {{
    font-family: {Typography.FONT_SANS};
    font-size: {Typography.SIZE_BODY};
    color: #E2E8F0;
}}

QWebEngineView {{
    background-color: #FFFFFF;
}}

/* ========================================================== */
/* Top Level Tab Strip Bar                                    */
/* ========================================================== */
#top_tab_strip {{
    background-color: {Colors.BG_CANVAS};
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    padding-top: 6px;
    padding-left: 10px;
    padding-right: 10px;
}}

QTabBar {{
    background-color: transparent;
    qproperty-drawBase: 0;
    border: none;
}}

QTabBar::tab {{
    background-color: {Colors.SURFACE_1};
    color: {Colors.TEXT_SECONDARY};
    padding: 7px 14px 7px 12px;
    margin-right: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    min-width: 140px;
    max-width: 230px;
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-bottom: none;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background: {Gradients.SURFACE_CARD_SELECTED};
    color: #FFFFFF;
    font-weight: 700;
    border-top: 2px solid {Colors.ACCENT_ORANGE};
    border-left: 1px solid {Colors.BORDER_DEFAULT};
    border-right: 1px solid {Colors.BORDER_DEFAULT};
}}

QTabBar::tab:hover:!selected {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.TEXT_PRIMARY};
    border-top: 1px solid {Colors.BORDER_HOVER};
}}

QTabBar::close-button {{
    subcontrol-position: right;
    margin-right: 4px;
    border-radius: 8px;
    padding: 2px;
}}

QTabBar::close-button:hover {{
    background-color: rgba(239, 68, 68, 0.35);
}}

/* New Tab Button next to tabs */
QPushButton#new_tab_btn {{
    background-color: {Colors.SURFACE_1};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    padding: 5px 10px;
    color: {Colors.TEXT_SECONDARY};
    margin-left: 4px;
    margin-bottom: 2px;
}}

QPushButton#new_tab_btn:hover {{
    background-color: {Colors.SURFACE_2};
    color: #FFFFFF;
    border: 1px solid {Colors.ACCENT_CYAN};
}}

/* ========================================================== */
/* Navigation Toolbar (Seamless directly below tab bar)      */
/* ========================================================== */
#nav_toolbar {{
    background: {Gradients.SURFACE_HEADER};
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    padding: 6px 14px;
}}

/* Navigation action buttons */
QPushButton.nav-btn {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 6px 10px;
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton.nav-btn:hover {{
    background-color: {Colors.SURFACE_2};
    border: 1px solid {Colors.BORDER_DEFAULT};
    color: #FFFFFF;
}}

QPushButton.nav-btn:pressed {{
    background-color: {Colors.BG_CANVAS};
}}

/* ========================================================== */
/* True Pill Omnibox Frame (Fully Rounded Capsule)           */
/* ========================================================== */
#omnibox_capsule {{
    background-color: {Colors.BG_BASE};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 19px;
    min-height: 38px;
    max-height: 38px;
    padding-left: 14px;
    padding-right: 12px;
}}

#omnibox_capsule:hover {{
    border: 1px solid {Colors.BORDER_HOVER};
    background-color: #111622;
}}

QLineEdit#omnibox_input {{
    background-color: transparent;
    border: none;
    padding: 2px 8px;
    color: {Colors.TEXT_PRIMARY};
    font-size: 13.5px;
    selection-background-color: {Colors.ACCENT_ORANGE};
}}

QLineEdit#omnibox_input:focus {{
    outline: none;
}}

QLabel#ssl_icon_lbl {{
    color: {Colors.STATUS_SUCCESS};
    font-size: 13px;
    margin-right: 2px;
}}

QPushButton#bookmark_btn {{
    background-color: transparent;
    border: none;
    border-radius: 12px;
    padding: 5px;
    color: {Colors.TEXT_MUTED};
}}

QPushButton#bookmark_btn:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    color: {Colors.STATUS_WARNING};
}}

/* ========================================================== */
/* Brave Shields Pill Badge & Action Buttons                  */
/* ========================================================== */
QPushButton#shield_btn {{
    background: {Gradients.PRIMARY_FLAME};
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    border-radius: 16px;
    padding: 6px 16px;
    border: 1px solid rgba(255, 255, 255, 0.22);
}}

QPushButton#shield_btn:hover {{
    background: {Gradients.PRIMARY_FLAME_HOVER};
    border: 1px solid rgba(255, 255, 255, 0.4);
}}

QPushButton#shield_btn:pressed {{
    background: {Gradients.PRIMARY_FLAME_PRESSED};
}}

/* Profiles Dashboard Action Pill */
QPushButton#dashboard_btn {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 14px;
    padding: 5px 14px;
    font-weight: 600;
    font-size: 12px;
}}

QPushButton#dashboard_btn:hover {{
    background-color: {Colors.SURFACE_3};
    border-color: {Colors.BORDER_HOVER};
    color: #FFFFFF;
}}

QPushButton#dashboard_btn:pressed {{
    background-color: {Colors.SURFACE_1};
}}

/* Cyber Security Lock Pill */
QPushButton#lock_btn {{
    background: {Gradients.CYBER_CYAN};
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    border-radius: 16px;
    padding: 6px 16px;
    border: 1px solid rgba(255, 255, 255, 0.22);
}}

QPushButton#lock_btn:hover {{
    background: {Gradients.CYBER_CYAN_HOVER};
    border: 1px solid rgba(255, 255, 255, 0.4);
}}

QPushButton#lock_btn:pressed {{
    background: {Gradients.CYBER_CYAN_PRESSED};
}}

/* ========================================================== */
/* Floating Link Hover Tooltip (Modern overlay)               */
/* ========================================================== */
QLabel#floating_link_tooltip {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.TEXT_SECONDARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 11px;
}}

/* ========================================================== */
/* Modern Dark Context Menu                                   */
/* ========================================================== */
QMenu {{
    background-color: {Colors.SURFACE_OVERLAY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: {Radii.MD};
    padding: 6px;
    color: {Colors.TEXT_PRIMARY};
    font-size: 13px;
}}

QMenu::item {{
    padding: 8px 24px 8px 14px;
    border-radius: {Radii.SM};
    background-color: transparent;
}}

QMenu::item:selected {{
    background-color: {Colors.SURFACE_3};
    color: {Colors.ACCENT_CYAN};
}}

QMenu::item:disabled {{
    color: {Colors.TEXT_MUTED};
}}

QMenu::separator {{
    height: 1px;
    background-color: {Colors.BORDER_SUBTLE};
    margin: 5px 6px;
}}

QMenu::icon {{
    padding-left: 6px;
}}

/* ========================================================== */
/* Bookmarks Bar                                              */
/* ========================================================== */
#bookmarks_bar {{
    background-color: {Colors.SURFACE_1};
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    min-height: 32px;
    max-height: 34px;
    padding: 2px 12px;
}}

QPushButton.bookmark-bar-item {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    border: 1px solid transparent;
    border-radius: {Radii.PILL};
    padding: 4px 12px;
    font-size: 12px;
    text-align: left;
}}

QPushButton.bookmark-bar-item:hover {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
}}

/* ========================================================== */
/* Find In Page Floating Bar                                  */
/* ========================================================== */
#find_bar {{
    background-color: {Colors.SURFACE_OVERLAY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 12px;
    padding: 5px 10px;
}}

#find_input {{
    background-color: {Colors.BG_BASE};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    padding: 5px 10px;
    font-size: 12px;
    min-width: 190px;
}}

#find_input:focus {{
    border: 1px solid {Colors.ACCENT_CYAN};
}}

#find_match_lbl {{
    color: {Colors.TEXT_SECONDARY};
    font-size: 12px;
    padding: 0 6px;
}}

/* ========================================================== */
/* Zoom Indicator Badge in Omnibox                            */
/* ========================================================== */
QLabel#zoom_badge {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.ACCENT_CYAN};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}}

/* ========================================================== */
/* Modern Dark Dialogs & Form Elements                        */
/* ========================================================== */
QDialog {{
    background-color: {Colors.BG_CANVAS};
    color: {Colors.TEXT_PRIMARY};
}}

QListWidget {{
    background-color: {Colors.SURFACE_1};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: {Radii.MD};
    color: #E2E8F0;
    padding: 6px;
}}

QListWidget::item {{
    padding: 9px 12px;
    border-radius: {Radii.SM};
    margin-bottom: 3px;
}}

QListWidget::item:selected {{
    background-color: {Colors.SURFACE_3};
    color: {Colors.ACCENT_CYAN};
}}

QListWidget::item:hover:!selected {{
    background-color: {Colors.SURFACE_2};
}}

QLineEdit.dialog-search {{
    background-color: {Colors.SURFACE_1};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 18px;
    color: {Colors.TEXT_PRIMARY};
    padding: 8px 16px;
    font-size: 13px;
}}

QLineEdit.dialog-search:focus {{
    border: 1px solid {Colors.ACCENT_ORANGE};
    background-color: #121724;
}}

QPushButton.dialog-btn-primary {{
    background: {Gradients.PRIMARY_FLAME};
    color: #FFFFFF;
    font-weight: 700;
    border-radius: 17px;
    padding: 8px 20px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    min-height: 18px;
}}

QPushButton.dialog-btn-primary:hover {{
    background: {Gradients.PRIMARY_FLAME_HOVER};
    border: 1px solid rgba(255, 255, 255, 0.35);
}}

QPushButton.dialog-btn-secondary {{
    background-color: {Colors.SURFACE_2};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 17px;
    padding: 8px 20px;
    min-height: 18px;
}}

QPushButton.dialog-btn-secondary:hover {{
    background-color: {Colors.SURFACE_3};
    color: #FFFFFF;
    border-color: {Colors.BORDER_HOVER};
}}

QPushButton.dialog-btn-danger {{
    background: {Gradients.DANGER_CRIMSON};
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 17px;
    font-weight: 700;
    padding: 8px 20px;
    min-height: 18px;
}}

QPushButton.dialog-btn-danger:hover {{
    background: {Gradients.DANGER_CRIMSON_HOVER};
}}

/* Global Checkbox Style */
QCheckBox {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {Colors.BORDER_DEFAULT};
    background: {Colors.SURFACE_2};
}}

QCheckBox::indicator:hover {{
    border-color: {Colors.BORDER_HOVER};
}}

QCheckBox::indicator:checked {{
    background-color: {Colors.ACCENT_ORANGE};
    border-color: {Colors.ACCENT_ORANGE};
    image: url(/mnt/storage/aplikasi/yourbrowser/assets/icons/ui/check_white.png);
}}

/* ========================================================== */
/* Sleek Rounded Scrollbars                                   */
/* ========================================================== */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {Colors.SURFACE_3};
    min-height: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {Colors.BORDER_HOVER};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {Colors.SURFACE_3};
    min-width: 24px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {Colors.BORDER_HOVER};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""


def get_theme_stylesheet(theme_mode: str = "brave_dark", accent_color: str = "orange") -> str:
    """Generate dynamic stylesheet based on user customization settings."""
    # Resolve accent colors
    accent_map = {
        "orange": "#FF5500",
        "cyan": "#06B6D4",
        "emerald": "#10B981",
        "purple": "#A855F7"
    }
    accent_hex = accent_map.get(accent_color, "#FF5500")

    if theme_mode == "light":
        return f"""
QMainWindow {{
    background-color: #F1F5F9;
    color: #0F172A;
}}
QMainWindow, QDialog, QMenu, QTabBar, QLabel, QLineEdit, QPushButton, QListWidget, QGroupBox, QComboBox, QProgressBar {{
    font-family: {Typography.FONT_SANS};
    font-size: {Typography.SIZE_BODY};
    color: #0F172A;
}}
QWebEngineView {{
    background-color: #FFFFFF;
}}
#top_tab_strip {{
    background-color: #E2E8F0;
    border-bottom: 1px solid #CBD5E1;
    padding-top: 6px;
    padding-left: 10px;
    padding-right: 10px;
}}
QTabBar::tab {{
    background-color: #F8FAFC;
    color: #475569;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    min-width: 140px;
    max-width: 230px;
    border: 1px solid #CBD5E1;
    border-bottom: none;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: #FFFFFF;
    color: #0F172A;
    font-weight: 700;
    border-top: 2px solid {accent_hex};
}}
#nav_toolbar {{
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 6px 12px;
}}
#omnibox_capsule {{
    background-color: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 19px;
    min-height: 38px;
    max-height: 38px;
    padding-left: 12px;
    padding-right: 12px;
}}
#omnibox_capsule:focus-within {{
    border: 1.5px solid {accent_hex};
    background-color: #FFFFFF;
}}
QLineEdit#omnibox {{
    background: transparent;
    border: none;
    color: #0F172A;
    font-size: 13.5px;
}}
QPushButton.nav-btn, QPushButton#new_tab_btn {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 17px;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
}}
QPushButton.nav-btn:hover, QPushButton#new_tab_btn:hover {{
    background-color: #E2E8F0;
    border: 1px solid #CBD5E1;
}}
#bookmarks_bar {{
    background-color: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
    min-height: 30px;
}}
QPushButton.bookmark-bar-item {{
    background-color: transparent;
    color: #334155;
    border: 1px solid transparent;
    border-radius: 14px;
    padding: 3px 10px;
    font-size: 12px;
}}
QPushButton.bookmark-bar-item:hover {{
    background-color: #E2E8F0;
    border-color: #CBD5E1;
}}
"""
    elif theme_mode == "cyber_dark":
        bg_canvas = "#050B14"
        bg_card = "#0D1829"
        border_subtle = "#15243B"
    elif theme_mode == "midnight":
        bg_canvas = "#000000"
        bg_card = "#0A0A0A"
        border_subtle = "#1A1A1A"
    else:  # brave_dark
        bg_canvas = Colors.BG_CANVAS
        bg_card = Colors.SURFACE_1
        border_subtle = Colors.BORDER_SUBTLE

    # Replace accent line in default theme with configured accent
    sheet = BRAVE_THEME_QSS
    if accent_hex != "#FF5500":
        sheet = sheet.replace(Colors.ACCENT_ORANGE, accent_hex)
    if bg_canvas != Colors.BG_CANVAS:
        sheet = sheet.replace(Colors.BG_CANVAS, bg_canvas)
        sheet = sheet.replace(Colors.SURFACE_1, bg_card)
        sheet = sheet.replace(Colors.BORDER_SUBTLE, border_subtle)

    return sheet

