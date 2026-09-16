"""
YourBrowser UI - Cyber Obsidian Lock Overlay & Password Protection Modal
Unified with Design System tokens, pill buttons, and cyber security gradients.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, pill_badge, rounded_input
)


class SetPasswordDialog(QDialog):
    """Modern modal dialog to set or modify password protection for a tab."""

    def __init__(self, tab_title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Protect Tab with Password")
        self.tab_title = tab_title
        self.password = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.LG};
            }}
            QLabel.header-title {{
                font-size: {Typography.SIZE_SUBTITLE};
                font-weight: 700;
                color: {Colors.ACCENT_CYAN};
            }}
            QLabel.desc-text {{
                font-size: 13px;
                color: {Colors.TEXT_SECONDARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel(f"🔒 Lock Tab Protection", self)
        title.setProperty("class", "header-title")
        layout.addWidget(title)

        import html
        safe_title = html.escape(self.tab_title[:30] + ("..." if len(self.tab_title) > 30 else ""))
        desc = QLabel(self)
        desc.setProperty("class", "desc-text")
        desc.setWordWrap(True)
        desc.setTextFormat(Qt.TextFormat.RichText)
        desc.setText(
            f"<div style='color:{Colors.TEXT_SECONDARY}; font-size:13px; margin-bottom: 6px;'>"
            f"Set a password or PIN for tab: <b style='color:#FFFFFF;'>\"{safe_title}\"</b><br><br>"
            f"Contents will be completely hidden behind an encrypted lock screen until unlocked."
            f"</div>"
        )
        layout.addWidget(desc)

        self.input_pwd = QLineEdit(self)
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Enter password or PIN...")
        self.input_pwd.setStyleSheet(rounded_input(38, Radii.SM))
        layout.addWidget(self.input_pwd)

        self.input_confirm = QLineEdit(self)
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setPlaceholderText("Confirm password or PIN...")
        self.input_confirm.setStyleSheet(rounded_input(38, Radii.SM))
        layout.addWidget(self.input_confirm)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setStyleSheet(pill_button_secondary(height=36))
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        save_btn = QPushButton("Protect && Lock", self)
        save_btn.setStyleSheet(pill_button_primary(
            gradient=Gradients.CYBER_CYAN,
            gradient_hover=Gradients.CYBER_CYAN_HOVER,
            gradient_pressed=Gradients.CYBER_CYAN_PRESSED,
            height=36
        ))
        save_btn.clicked.connect(self.on_save)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)
        self.resize(460, 340)

    def on_save(self):
        pwd = self.input_pwd.text().strip()
        confirm = self.input_confirm.text().strip()
        if not pwd:
            QMessageBox.warning(self, "Validation Error", "Password cannot be empty!")
            return
        if pwd != confirm:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match!")
            return
        self.password = pwd
        self.accept()


class LockedTabOverlay(QWidget):
    """Ultra-modern Obsidian & Cyber lock screen displayed over protected tabs."""
    unlocked = pyqtSignal()

    def __init__(self, tab_id, security_manager, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.security_manager = security_manager
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CANVAS};
            }}
            #lock_card {{
                background: {Gradients.SURFACE_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.XL};
                padding: 36px 40px;
                max-width: 440px;
            }}
            QLabel.icon-shield {{
                font-size: 56px;
            }}
            QLabel.lock-title {{
                font-size: 22px;
                font-weight: 800;
                color: {Colors.TEXT_PRIMARY};
                margin-top: 4px;
            }}
            QLabel.lock-subtitle {{
                font-size: 13px;
                color: {Colors.TEXT_SECONDARY};
                margin-bottom: 8px;
            }}
            QLabel.badge-status {{
                color: {Colors.ACCENT_CYAN};
                background-color: {Colors.SURFACE_3};
                border: 1px solid {Colors.ACCENT_CYAN};
                border-radius: {Radii.PILL};
                padding: 4px 14px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setObjectName("lock_card")
        c_layout = QVBoxLayout(card)
        c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(14)

        icon_lbl = QLabel("🔐", card)
        icon_lbl.setProperty("class", "icon-shield")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(icon_lbl)

        badge = QLabel("ENCRYPTED SESSION", card)
        badge.setProperty("class", "badge-status")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Tab is Password Protected", card)
        title.setProperty("class", "lock-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(title)

        sub = QLabel("Enter password or PIN to decrypt and access web contents.", card)
        sub.setProperty("class", "lock-subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(sub)

        self.input_pwd = QLineEdit(card)
        self.input_pwd.setObjectName("pwd_box")
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Enter password / PIN...")
        self.input_pwd.setStyleSheet(rounded_input(42, Radii.SM))
        self.input_pwd.returnPressed.connect(self.on_unlock)
        c_layout.addWidget(self.input_pwd)

        unlock_btn = QPushButton("Unlock Session", card)
        unlock_btn.setStyleSheet(pill_button_primary(
            gradient=Gradients.CYBER_CYAN,
            gradient_hover=Gradients.CYBER_CYAN_HOVER,
            gradient_pressed=Gradients.CYBER_CYAN_PRESSED,
            height=40,
            font_size="13.5px"
        ))
        unlock_btn.clicked.connect(self.on_unlock)
        c_layout.addWidget(unlock_btn)

        layout.addWidget(card)

    def on_unlock(self):
        candidate = self.input_pwd.text().strip()
        if self.security_manager.verify_tab_password(self.tab_id, candidate):
            self.unlocked.emit()
            self.hide()
        else:
            QMessageBox.critical(self, "Access Denied", "Incorrect tab password!")
            self.input_pwd.clear()
            self.input_pwd.setFocus()
