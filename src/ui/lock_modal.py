"""
YourBrowser UI - Tab Password Protection & Lock Overlay
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class SetPasswordDialog(QDialog):
    """Dialog to set or modify password for a tab."""
    
    def __init__(self, tab_title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lock Tab with Password")
        self.tab_title = tab_title
        self.password = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #161920;
                color: #FFFFFF;
            }
            QLabel {
                color: #E2E8F0;
            }
            QLineEdit {
                background-color: #0F1115;
                border: 1px solid #38BDF8;
                border-radius: 8px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #38BDF8;
                color: #0F1115;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7DD3FC;
            }
            QPushButton.cancel {
                background-color: #334155;
                color: #E2E8F0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel(f"🔒 Set Password for Tab:\n\"{self.tab_title[:40]}...\"")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #38BDF8;")
        layout.addWidget(title)

        desc = QLabel("Enter a password or PIN to encrypt and protect this tab from unauthorized viewing:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.input_pwd = QLineEdit(self)
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Enter tab password / PIN...")
        layout.addWidget(self.input_pwd)

        self.input_confirm = QLineEdit(self)
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setPlaceholderText("Confirm password / PIN...")
        layout.addWidget(self.input_confirm)

        btn_box = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        save_btn = QPushButton("Protect Tab", self)
        save_btn.clicked.connect(self.on_save)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)
        self.resize(360, 240)

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
    """Overlay displayed over locked tabs requiring password entry to unlock."""
    unlocked = pyqtSignal()

    def __init__(self, tab_id, security_manager, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.security_manager = security_manager
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1115;
            }
            QLabel.lock-title {
                font-size: 20px;
                font-weight: bold;
                color: #38BDF8;
            }
            QLabel.lock-subtitle {
                font-size: 13px;
                color: #94A3B8;
            }
            QLineEdit {
                background-color: #1E222D;
                border: 2px solid #38BDF8;
                border-radius: 10px;
                padding: 12px 18px;
                color: #FFFFFF;
                font-size: 15px;
                max-width: 320px;
            }
            QPushButton.unlock-btn {
                background-color: #38BDF8;
                color: #0F1115;
                font-weight: bold;
                border-radius: 10px;
                padding: 12px 28px;
                font-size: 14px;
                border: none;
            }
            QPushButton.unlock-btn:hover {
                background-color: #7DD3FC;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        icon_lbl = QLabel("🔐", self)
        icon_lbl.setStyleSheet("font-size: 54px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_lbl)

        title = QLabel("This Tab is Password Protected", self)
        title.setProperty("class", "lock-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Enter password to decrypt and view web contents.", self)
        sub.setProperty("class", "lock-subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        self.input_pwd = QLineEdit(self)
        self.input_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd.setPlaceholderText("Enter Tab Password...")
        self.input_pwd.returnPressed.connect(self.on_unlock)
        layout.addWidget(self.input_pwd, alignment=Qt.AlignmentFlag.AlignCenter)

        unlock_btn = QPushButton("Unlock Tab", self)
        unlock_btn.setProperty("class", "unlock-btn")
        unlock_btn.clicked.connect(self.on_unlock)
        layout.addWidget(unlock_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_unlock(self):
        candidate = self.input_pwd.text().strip()
        if self.security_manager.verify_tab_password(self.tab_id, candidate):
            self.unlocked.emit()
            self.hide()
        else:
            QMessageBox.critical(self, "Access Denied", "Incorrect tab password!")
            self.input_pwd.clear()
