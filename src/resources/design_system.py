"""
YourBrowser Design System - Foundational Tokens & Styling Engine
Provides structured design tokens (Colors, Gradients, Shapes/Radii, Typography)
and QSS generator helpers for a cohesive, modern, and professional aesthetic.
"""


class Colors:
    # Canvas & Backgrounds
    BG_CANVAS = "#0B0E14"
    BG_BASE = "#0E121A"
    
    # Surfaces (Tiered elevation)
    SURFACE_1 = "#121622"  # Card / Panel container
    SURFACE_2 = "#181D2C"  # Raised components, hover states
    SURFACE_3 = "#22293D"  # Input fields, sub-panels
    SURFACE_OVERLAY = "#161B26"
    
    # Borders & Dividers
    BORDER_SUBTLE = "#1C2333"
    BORDER_DEFAULT = "#263045"
    BORDER_HOVER = "#3A4765"
    BORDER_ACTIVE = "#FF5500"
    
    # Typography
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    TEXT_INVERTED = "#0A0D14"
    
    # Functional & Semantic Accents
    ACCENT_ORANGE = "#FF5500"
    ACCENT_PINK = "#FF2A54"
    ACCENT_CYAN = "#06B6D4"
    ACCENT_BLUE = "#3B82F6"
    ACCENT_PURPLE = "#8B5CF6"
    ACCENT_INDIGO = "#6366F1"
    
    # Status Indicators
    STATUS_SUCCESS = "#10B981"
    STATUS_SUCCESS_BG = "#064E3B"
    STATUS_WARNING = "#F59E0B"
    STATUS_WARNING_BG = "#78350F"
    STATUS_DANGER = "#EF4444"
    STATUS_DANGER_BG = "#7F1D1D"


class Gradients:
    # Primary Brave Flame (Vibrant Sunset / Fire)
    PRIMARY_FLAME = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54)"
    PRIMARY_FLAME_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6A1F, stop:1 #FF4267)"
    PRIMARY_FLAME_PRESSED = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E04000, stop:1 #E01940)"
    
    # Cyber Cyan (Neon Blue / Vault / Security Accent)
    CYBER_CYAN = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #3B82F6)"
    CYBER_CYAN_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22D3EE, stop:1 #60A5FA)"
    CYBER_CYAN_PRESSED = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0891B2, stop:1 #2563EB)"
    
    # Emerald Glow (Shields Safe / Connected / Verified)
    EMERALD_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669)"
    EMERALD_GLOW_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981)"
    
    # Purple Stealth (Private / Incognito / Cryptographic Vault)
    PURPLE_STEALTH = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #6366F1)"
    PURPLE_STEALTH_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A78BFA, stop:1 #818CF8)"
    
    # Danger Crimson (Wipe, Kill Switch, Remove)
    DANGER_CRIMSON = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626)"
    DANGER_CRIMSON_HOVER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444)"

    # Deep Surface Gradients (Adds subtle high-end glass/obsidian depth)
    SURFACE_CARD = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161B28, stop:1 #10141F)"
    SURFACE_CARD_HOVER = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C2334, stop:1 #141926)"
    SURFACE_CARD_SELECTED = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222B3F, stop:1 #171E2D)"
    SURFACE_DIALOG = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141824, stop:1 #0C0F17)"
    SURFACE_HEADER = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #161C2B, stop:1 #101420)"


class Radii:
    # Corner Radii
    XS = "4px"
    SM = "8px"
    MD = "12px"
    LG = "16px"
    XL = "20px"
    PILL = "9999px"  # Full pill / capsule shape


class Typography:
    FONT_SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Ubuntu", sans-serif'
    FONT_MONO = '"JetBrains Mono", "Roboto Mono", Consolas, monospace'
    
    SIZE_TITLE = "20px"
    SIZE_SUBTITLE = "16px"
    SIZE_BODY = "13px"
    SIZE_SMALL = "12px"
    SIZE_BADGE = "11px"


# -----------------------------------------------------------------------------
# Component Style Helpers
# -----------------------------------------------------------------------------

def pill_button_primary(gradient: str = Gradients.PRIMARY_FLAME,
                        gradient_hover: str = Gradients.PRIMARY_FLAME_HOVER,
                        gradient_pressed: str = Gradients.PRIMARY_FLAME_PRESSED,
                        text_color: str = "#FFFFFF",
                        height: int = 34,
                        font_size: str = "12.5px") -> str:
    """Generate modern pill button style with vibrant gradient."""
    radius = height // 2
    return f"""
        QPushButton {{
            background: {gradient};
            color: {text_color};
            font-weight: 700;
            font-size: {font_size};
            border-radius: {radius}px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 0 18px;
            min-height: {height}px;
            max-height: {height}px;
        }}
        QPushButton:hover {{
            background: {gradient_hover};
            border: 1px solid rgba(255, 255, 255, 0.35);
        }}
        QPushButton:pressed {{
            background: {gradient_pressed};
        }}
        QPushButton:disabled {{
            background: #2D3748;
            color: #718096;
            border: none;
        }}
    """


def pill_button_secondary(height: int = 34, font_size: str = "12.5px") -> str:
    """Generate subtle secondary rounded button."""
    radius = height // 2
    return f"""
        QPushButton {{
            background-color: {Colors.SURFACE_2};
            color: {Colors.TEXT_PRIMARY};
            font-weight: 600;
            font-size: {font_size};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {radius}px;
            padding: 0 16px;
            min-height: {height}px;
            max-height: {height}px;
        }}
        QPushButton:hover {{
            background-color: {Colors.SURFACE_3};
            border-color: {Colors.BORDER_HOVER};
            color: #FFFFFF;
        }}
        QPushButton:pressed {{
            background-color: {Colors.SURFACE_1};
        }}
    """


def pill_badge(bg_color: str, text_color: str, font_size: str = "10.5px") -> str:
    """Generate rounded pill tag/badge."""
    return f"""
        background-color: {bg_color};
        color: {text_color};
        font-size: {font_size};
        font-weight: 700;
        padding: 3px 10px;
        border-radius: {Radii.PILL};
    """


def rounded_input(height: int = 36, radius: str = "10px") -> str:
    """Generate sleek modern input styling."""
    return f"""
        QLineEdit {{
            background-color: {Colors.BG_BASE};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {radius};
            padding: 6px 12px;
            color: {Colors.TEXT_PRIMARY};
            font-size: 13px;
            min-height: {height - 14}px;
        }}
        QLineEdit:hover {{
            border: 1px solid {Colors.BORDER_HOVER};
        }}
        QLineEdit:focus {{
            border: 1px solid {Colors.ACCENT_ORANGE};
            background-color: #101420;
        }}
    """
