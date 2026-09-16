"""
YourBrowser UI - Cyber Obsidian Lock Overlay & Password Protection Modal
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

class SetPasswordDialog(QDialog):
    """Modern modal dialog to set or modify password protection for a tab."""
    
    def __init__(self, tab_title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Protect Tab with Password")
        self.tab_title = tab_title
        self.password = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #121620;
                color: #FFFFFF;
                border: 1px solid #283347;
                border-radius: 16px;
            }
            QLabel.header-title {
                font-size: 16px;
                font-weight: 700;
                color: #38BDF8;
            }
            QLabel.desc-text {
                font-size: 13px;
                color: #94A3B8;
                line-height: 1.4;
            }
            QLineEdit {
                background-color: #0A0D14;
                border: 1px solid #283347;
                border-radius: 10px;
                padding: 10px 14px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #38BDF8;
                background-color: #0F131D;
            }
            QPushButton.primary-btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #38BDF8);
                color: #0A0D14;
                font-weight: 700;
                font-size: 13px;
                border-radius: 10px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton.primary-btn:hover {
                background: #38BDF8;
            }
            QPushButton.cancel-btn {
                background-color: #1E2535;
                color: #94A3B8;
                font-weight: 600;
                border-radius: 10px;
                padding: 10px 18px;
                border: 1px solid #2B3449;
            }
            QPushButton.cancel-btn:hover {
                background-color: #273045;
                color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(f"🔒 Lock Tab Protection", self)
        title.setProperty("class", "header-title")
        layout.addWidget(title)

        desc = QLabel(
            f"Set a password or PIN for tab:\n<b>\"{self.tab_title[:35]}...\"</b>\n"
            "Contents will be completely hidden behind an encrypted lock screen until unlocked.",
            self
        )
        desc.setProperty("class", "desc-text")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.input_pwd = QLineEdit(self)
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Enter password or PIN...")
        layout.addWidget(self.input_pwd)

        self.input_confirm = QLineEdit(self)
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setPlaceholderText("Confirm password or PIN...")
        layout.addWidget(self.input_confirm)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "cancel-btn")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        save_btn = QPushButton("Protect & Lock", self)
        save_btn.setProperty("class", "primary-btn")
        save_btn.clicked.connect(self.on_save)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)
        self.resize(380, 260)

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
        self.setStyleSheet("""
            QWidget {
                background-color: #0A0D14;
            }
            #lock_card {
                background-color: #131824;
                border: 1px solid #232D40;
                border-radius: 20px;
                padding: 36px 40px;
                max-width: 440px;
            }
            QLabel.icon-shield {
                font-size: 56px;
            }
            QLabel.lock-title {
                font-size: 22px;
                font-weight: 800;
                color: #F8FAFC;
                margin-top: 4px;
            }
            QLabel.lock-subtitle {
                font-size: 13px;
                color: #94A3B8;
                margin-bottom: 8px;
            }
            QLineEdit#pwd_box {
                background-color: #0A0D14;
                border: 1px solid #38BDF8;
                border-radius: 12px;
                padding: 12px 18px;
                color: #FFFFFF;
                font-size: 15px;
                selection-background-color: #38BDF8;
            }
            QLineEdit#pwd_box:focus {
                border: 2px solid #38BDF8;
                background-color: #0E131E;
            }
            QPushButton.unlock-btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #38BDF8);
                color: #0A0D14;
                font-weight: 800;
                font-size: 14px;
                border-radius: 12px;
                padding: 12px 28px;
                border: none;
            }
            QPushButton.unlock-btn:hover {
                background: #38BDF8;
            }
            QPushButton.unlock-btn:pressed {
                background: #0284C7;
            }
            QLabel.badge-status {
                color: #38BDF8;
                background-color: #17283C;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
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
        self.input_pwd.returnPressed.connect(self.on_unlock)
        c_layout.addWidget(self.input_pwd)

        unlock_btn = QPushButton("Unlock Session", card)
        unlock_btn.setProperty("class", "unlock-btn")
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
