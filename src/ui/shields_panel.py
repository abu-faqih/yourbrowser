"""
YourBrowser UI - Ultra-Modern Brave Shields Dropdown Panel
Unified with Design System tokens, pill toggles, and vibrant gradients.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt
from src.resources.design_system import Colors, Gradients, Radii, Typography


class ShieldsPopup(QDialog):
    """Modern Brave-style Shields popover with real-time telemetry card."""

    def __init__(self, interceptor, current_url="", parent=None):
        super().__init__(parent)
        self.interceptor = interceptor
        self.current_url = current_url
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: transparent;
            }}
            #card {{
                background: {Gradients.SURFACE_DIALOG};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.LG};
                padding: 18px;
            }}
            QLabel.brand-title {{
                font-size: 15px;
                font-weight: 700;
                color: {Colors.TEXT_PRIMARY};
            }}
            QLabel.domain-text {{
                font-size: 12px;
                color: {Colors.TEXT_SECONDARY};
            }}
            QPushButton.toggle-btn-on {{
                background: {Gradients.PRIMARY_FLAME};
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                padding: 6px 16px;
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton.toggle-btn-on:hover {{
                background: {Gradients.PRIMARY_FLAME_HOVER};
            }}
            QPushButton.toggle-btn-off {{
                background-color: {Colors.SURFACE_2};
                color: {Colors.TEXT_SECONDARY};
                font-weight: 700;
                font-size: 11px;
                padding: 6px 16px;
                border-radius: 14px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
            QPushButton.toggle-btn-off:hover {{
                background-color: {Colors.SURFACE_3};
                color: #FFFFFF;
            }}
            #metric_box {{
                background-color: {Colors.BG_BASE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radii.MD};
                padding: 16px;
                margin: 10px 0;
            }}
            QLabel.counter-number {{
                font-size: 36px;
                font-weight: 800;
                color: {Colors.ACCENT_ORANGE};
            }}
            QLabel.counter-label {{
                font-size: 12px;
                font-weight: 500;
                color: {Colors.TEXT_SECONDARY};
            }}
            QLabel.feature-item {{
                font-size: 12px;
                color: #E2E8F0;
                padding: 2px 0;
            }}
            QLabel.badge-green {{
                color: {Colors.STATUS_SUCCESS};
                font-weight: 700;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(10)

        # Header Row
        h_layout = QHBoxLayout()
        header_text_box = QVBoxLayout()
        header_text_box.setSpacing(2)

        brand_title = QLabel("Brave Shields Pro", card)
        brand_title.setProperty("class", "brand-title")
        header_text_box.addWidget(brand_title)

        domain = "This Site"
        if self.current_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(self.current_url)
                domain = parsed.hostname or "Current Page"
            except Exception:
                pass

        domain_lbl = QLabel(domain, card)
        domain_lbl.setProperty("class", "domain-text")
        header_text_box.addWidget(domain_lbl)
        h_layout.addLayout(header_text_box)
        h_layout.addStretch()

        self.toggle_btn = QPushButton("SHIELDS UP", card)
        self.toggle_btn.setProperty("class", "toggle-btn-on")
        self.toggle_btn.clicked.connect(self.on_toggle_shields)
        h_layout.addWidget(self.toggle_btn)
        c_layout.addLayout(h_layout)

        # Main Metric Box
        metric_box = QFrame(card)
        metric_box.setObjectName("metric_box")
        m_layout = QVBoxLayout(metric_box)
        m_layout.setSpacing(2)
        m_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.counter_lbl = QLabel(str(self.interceptor.blocked_count), metric_box)
        self.counter_lbl.setProperty("class", "counter-number")
        self.counter_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_layout.addWidget(self.counter_lbl)

        lbl_desc = QLabel("Trackers & Ads Blocked", metric_box)
        lbl_desc.setProperty("class", "counter-label")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        m_layout.addWidget(lbl_desc)

        c_layout.addWidget(metric_box)

        # Active Protections Checklist
        list_box = QVBoxLayout()
        list_box.setSpacing(6)

        def add_feature(text):
            row = QHBoxLayout()
            check = QLabel("✓", card)
            check.setProperty("class", "badge-green")
            row.addWidget(check)
            txt = QLabel(text, card)
            txt.setProperty("class", "feature-item")
            row.addWidget(txt)
            row.addStretch()
            list_box.addLayout(row)

        add_feature("Cross-site trackers & telemetry blocked")
        add_feature("Aggressive cosmetic & banner filtering")
        add_feature("Strict browser fingerprinting defense")
        add_feature("Anti-clickjacking & popunder suppressor")

        c_layout.addLayout(list_box)
        layout.addWidget(card)
        self.resize(320, 275)

    def on_toggle_shields(self):
        self.interceptor.shields_enabled = not self.interceptor.shields_enabled
        if self.interceptor.shields_enabled:
            self.toggle_btn.setText("SHIELDS UP")
            self.toggle_btn.setProperty("class", "toggle-btn-on")
            self.toggle_btn.setStyleSheet("")
        else:
            self.toggle_btn.setText("SHIELDS DOWN")
            self.toggle_btn.setProperty("class", "toggle-btn-off")
            self.toggle_btn.setStyleSheet("")
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
