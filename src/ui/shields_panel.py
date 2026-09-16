"""
YourBrowser UI - Brave Shields Interactive Panel
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget
)
from PyQt6.QtCore import Qt

class ShieldsPopup(QDialog):
    """Interactive Brave Shields dropdown modal."""
    
    def __init__(self, interceptor, current_url="", parent=None):
        super().__init__(parent)
        self.interceptor = interceptor
        self.current_url = current_url
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            #container {
                background-color: #1E222D;
                border: 1px solid #3B4254;
                border-radius: 12px;
                padding: 16px;
            }
            QLabel.title {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QLabel.counter {
                font-size: 32px;
                font-weight: 800;
                color: #FF5500;
            }
            QLabel.subtitle {
                font-size: 12px;
                color: #94A3B8;
            }
            QPushButton.toggle-btn {
                background-color: #FF5500;
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton.toggle-btn.off {
                background-color: #475569;
                color: #CBD5E1;
            }
            QFrame.divider {
                background-color: #2D3344;
                max-height: 1px;
                margin: 10px 0;
            }
            QLabel.badge {
                background-color: #2D3344;
                color: #38BDF8;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QFrame(self)
        container.setObjectName("container")
        c_layout = QVBoxLayout(container)

        # Header with Lion branding
        h_layout = QHBoxLayout()
        title_lbl = QLabel("🛡️ Brave Shields", container)
        title_lbl.setProperty("class", "title")
        h_layout.addWidget(title_lbl)
        h_layout.addStretch()

        self.toggle_btn = QPushButton("SHIELDS UP", container)
        self.toggle_btn.setProperty("class", "toggle-btn")
        self.toggle_btn.clicked.connect(self.on_toggle_shields)
        h_layout.addWidget(self.toggle_btn)
        c_layout.addLayout(h_layout)

        # Divider
        div = QFrame(container)
        div.setProperty("class", "divider")
        c_layout.addWidget(div)

        # Counter Section
        count_layout = QVBoxLayout()
        self.count_lbl = QLabel(str(self.interceptor.blocked_count), container)
        self.count_lbl.setProperty("class", "counter")
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_layout.addWidget(self.count_lbl)

        sub_lbl = QLabel("Trackers & Ads Blocked", container)
        sub_lbl.setProperty("class", "subtitle")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_layout.addWidget(sub_lbl)
        c_layout.addLayout(count_layout)

        # Features List
        div2 = QFrame(container)
        div2.setProperty("class", "divider")
        c_layout.addWidget(div2)

        feat1 = QLabel("✓ Aggressive Ad & Tracker Blocking", container)
        feat1.setStyleSheet("color: #10B981; font-weight: 500;")
        c_layout.addWidget(feat1)

        feat2 = QLabel("✓ Strict Fingerprinting Protection", container)
        feat2.setStyleSheet("color: #10B981; font-weight: 500;")
        c_layout.addWidget(feat2)

        feat3 = QLabel("✓ Popunder & Redirect Neutralizer", container)
        feat3.setStyleSheet("color: #10B981; font-weight: 500;")
        c_layout.addWidget(feat3)

        layout.addWidget(container)
        self.resize(300, 240)

    def on_toggle_shields(self):
        self.interceptor.shields_enabled = not self.interceptor.shields_enabled
        if self.interceptor.shields_enabled:
            self.toggle_btn.setText("SHIELDS UP")
            self.toggle_btn.setStyleSheet("background-color: #FF5500;")
        else:
            self.toggle_btn.setText("SHIELDS DOWN")
            self.toggle_btn.setStyleSheet("background-color: #475569;")
