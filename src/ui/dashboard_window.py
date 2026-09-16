"""
YourBrowser UI - Profile Dashboard Window
Ultra-Modern Brave Obsidian Dark aesthetic for managing isolated browser profiles,
password authentication, hidden profiles toggle (Ctrl+H), and session launching.
"""

import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDialog, QCheckBox,
    QGridLayout, QScrollArea, QFrame, QMessageBox,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QFont

from src.core.profile_manager import ProfileManager, DEFAULT_AVATAR_COLORS
from src.resources.style import BRAVE_THEME_QSS
from src.resources.icons import create_svg_icon


class ProfilePasswordDialog(QDialog):
    """Dialog asking for profile password before unlocking."""

    def __init__(self, profile_name: str, profile_id: str, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.profile_manager = profile_manager
        self.setWindowTitle("Unlock Profile")
        self.setFixedSize(380, 240)
        self.setStyleSheet(BRAVE_THEME_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title_lbl = QLabel(f"🔒 Unlock '{profile_name}'", self)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("This profile is password-protected. Enter password to continue:", self)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(desc_lbl)

        self.pwd_input = QLineEdit(self)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter profile password...")
        self.pwd_input.setFixedHeight(36)
        self.pwd_input.returnPressed.connect(self.verify_and_accept)
        layout.addWidget(self.pwd_input)

        self.error_lbl = QLabel("", self)
        self.error_lbl.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 600;")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        unlock_btn = QPushButton("Unlock & Open", self)
        unlock_btn.setFixedHeight(34)
        unlock_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5500;
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 6px;
                border: none;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #FF661A;
            }
        """)
        unlock_btn.clicked.connect(self.verify_and_accept)
        btn_row.addWidget(unlock_btn)

        layout.addLayout(btn_row)
        self.pwd_input.setFocus()

    def verify_and_accept(self):
        candidate = self.pwd_input.text()
        if self.profile_manager.verify_password(self.profile_id, candidate):
            self.accept()
        else:
            self.error_lbl.setText("Incorrect password. Please try again.")
            self.error_lbl.show()
            self.pwd_input.selectAll()
            self.pwd_input.setFocus()


class CreateProfileDialog(QDialog):
    """Dialog for creating a new isolated browser profile."""

    def __init__(self, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.created_profile: Optional[Dict[str, Any]] = None

        self.setWindowTitle("Create New Profile")
        self.setFixedSize(420, 380)
        self.setStyleSheet(BRAVE_THEME_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title_lbl = QLabel("👤 Add New Browser Profile", self)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        # Profile Name
        name_lbl = QLabel("Profile Name:", self)
        name_lbl.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 12px;")
        layout.addWidget(name_lbl)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("e.g. Work, Trading, Personal, Stealth...")
        self.name_input.setFixedHeight(36)
        layout.addWidget(self.name_input)

        # Password (Optional)
        pwd_lbl = QLabel("Password Protection (Optional):", self)
        pwd_lbl.setStyleSheet("color: #94A3B8; font-weight: 600; font-size: 12px; margin-top: 4px;")
        layout.addWidget(pwd_lbl)

        self.pwd_input = QLineEdit(self)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Leave blank for no password")
        self.pwd_input.setFixedHeight(36)
        layout.addWidget(self.pwd_input)

        # Hidden Checkbox
        self.hide_chk = QCheckBox("Hide this profile (Toggle view with Ctrl+H)", self)
        self.hide_chk.setStyleSheet("color: #CBD5E1; font-size: 13px; margin-top: 4px;")
        layout.addWidget(self.hide_chk)

        self.error_lbl = QLabel("", self)
        self.error_lbl.setStyleSheet("color: #EF4444; font-size: 12px;")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Create Profile", self)
        save_btn.setFixedHeight(34)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5500;
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 6px;
                border: none;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #FF661A;
            }
        """)
        save_btn.clicked.connect(self.on_create)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        self.name_input.setFocus()

    def on_create(self):
        name = self.name_input.text().strip()
        if not name:
            self.error_lbl.setText("Please enter a valid profile name.")
            self.error_lbl.show()
            return

        pwd = self.pwd_input.text()
        is_hidden = self.hide_chk.isChecked()

        self.created_profile = self.profile_manager.create_profile(
            name=name,
            password=pwd if pwd else None,
            is_hidden=is_hidden
        )
        self.accept()


class ProfileCard(QFrame):
    """Interactive visual card representing a single profile."""

    def __init__(self, profile: Dict[str, Any], on_select, on_delete, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.on_select = on_select
        self.on_delete = on_delete

        self.setObjectName("profile_card")
        self.setFixedSize(220, 240)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #profile_card {
                background-color: #12151D;
                border: 1px solid #1C202C;
                border-radius: 12px;
            }
            #profile_card:hover {
                background-color: #181D28;
                border: 1px solid #FF5500;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar Circle
        avatar_color = profile.get("avatar_color", "#FF5500")
        initial = (profile.get("name", "P")[:1]).upper()
        avatar_lbl = QLabel(initial, self)
        avatar_lbl.setFixedSize(64, 64)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setStyleSheet(f"""
            background-color: {avatar_color};
            color: #FFFFFF;
            font-size: 26px;
            font-weight: 800;
            border-radius: 32px;
        """)
        layout.addWidget(avatar_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Profile Name
        name_lbl = QLabel(profile.get("name", "Profile"), self)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #F8FAFC;")
        layout.addWidget(name_lbl)

        # Status Badges
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(6)
        badges_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if profile.get("has_password", False):
            lock_badge = QLabel("🔒 Locked", self)
            lock_badge.setStyleSheet("""
                background-color: #3B1C1C;
                color: #F87171;
                font-size: 10px;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            badges_layout.addWidget(lock_badge)

        if profile.get("is_hidden", False):
            hidden_badge = QLabel("👁️ Hidden", self)
            hidden_badge.setStyleSheet("""
                background-color: #1E293B;
                color: #38BDF8;
                font-size: 10px;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 4px;
            """)
            badges_layout.addWidget(hidden_badge)

        layout.addLayout(badges_layout)

        # Launch Button
        launch_btn = QPushButton("Open Profile", self)
        launch_btn.setFixedHeight(30)
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #1C202C;
                color: #E2E8F0;
                font-weight: 600;
                border: 1px solid #283042;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FF5500;
                color: #FFFFFF;
                border-color: #FF5500;
            }
        """)
        launch_btn.clicked.connect(lambda: self.on_select(self.profile))
        layout.addWidget(launch_btn)

        # Delete action button
        del_btn = QPushButton("Delete", self)
        del_btn.setFixedHeight(22)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                font-size: 11px;
                border: none;
            }
            QPushButton:hover {
                color: #EF4444;
                text-decoration: underline;
            }
        """)
        del_btn.clicked.connect(lambda: self.on_delete(self.profile))
        layout.addWidget(del_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_select(self.profile)
        super().mousePressEvent(event)


class DashboardWindow(QMainWindow):
    """Main Dashboard Window for Profile Selection & Management."""

    def __init__(self, profile_manager: Optional[ProfileManager] = None, initial_url: Optional[str] = None):
        super().__init__()
        self.profile_manager = profile_manager if profile_manager else ProfileManager()
        self.initial_url = initial_url
        self.show_hidden = False
        self.active_browser_window = None

        self.setWindowTitle("YourBrowser - Profiles & Dashboard")
        self.resize(960, 680)
        self.setStyleSheet(BRAVE_THEME_QSS)

        self.setup_ui()
        self.setup_shortcuts()
        self.refresh_profiles()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(32, 28, 32, 28)
        self.main_layout.setSpacing(20)

        # Header Bar
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Logo & App Title
        logo_box = QHBoxLayout()
        logo_box.setSpacing(10)
        shield_icon = QLabel("🛡️", header_widget)
        shield_icon.setStyleSheet("font-size: 28px;")
        logo_box.addWidget(shield_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        app_title = QLabel("YourBrowser", header_widget)
        app_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        sub_title = QLabel("Isolated Profiles & Vault Dashboard", header_widget)
        sub_title.setStyleSheet("font-size: 12px; color: #94A3B8;")
        title_col.addWidget(app_title)
        title_col.addWidget(sub_title)
        logo_box.addLayout(title_col)

        header_layout.addLayout(logo_box)
        header_layout.addStretch()

        # Hidden profile status badge
        self.hidden_status_lbl = QLabel("", header_widget)
        self.hidden_status_lbl.setStyleSheet("""
            background-color: #1E293B;
            color: #38BDF8;
            font-size: 11px;
            font-weight: 700;
            padding: 5px 10px;
            border-radius: 6px;
            border: 1px solid #38BDF8;
        """)
        self.hidden_status_lbl.hide()
        header_layout.addWidget(self.hidden_status_lbl)

        # Add Profile Button
        self.add_profile_btn = QPushButton("+ New Profile", header_widget)
        self.add_profile_btn.setFixedHeight(36)
        self.add_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5500;
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 6px;
                padding: 0 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF661A;
            }
        """)
        self.add_profile_btn.clicked.connect(self.open_create_profile_dialog)
        header_layout.addWidget(self.add_profile_btn)

        self.main_layout.addWidget(header_widget)

        # Divider line
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #1C202C;")
        self.main_layout.addWidget(divider)

        # Scrollable Profiles Content Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 10, 0, 10)
        self.content_layout.setSpacing(16)
        self.scroll_area.setWidget(self.content_widget)

        self.main_layout.addWidget(self.scroll_area, stretch=1)

        # Footer shortcut hint
        footer_lbl = QLabel("💡 Tip: Press Ctrl+H to toggle visibility of hidden profiles", self)
        footer_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(footer_lbl)

    def setup_shortcuts(self):
        """Shortcut Ctrl+H to toggle hidden profiles."""
        self.toggle_hidden_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self.toggle_hidden_shortcut.activated.connect(self.toggle_hidden_profiles)

    def toggle_hidden_profiles(self):
        """Toggle viewing of hidden profiles."""
        self.show_hidden = not self.show_hidden
        if self.show_hidden:
            self.hidden_status_lbl.setText("👁️ Hidden Profiles: Visible")
            self.hidden_status_lbl.show()
        else:
            self.hidden_status_lbl.hide()
        self.refresh_profiles()

    def refresh_profiles(self):
        """Clear and redraw profile cards or onboarding empty state."""
        # Clear existing layout items
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        profiles = self.profile_manager.list_profiles(include_hidden=self.show_hidden)
        all_profiles_count = len(self.profile_manager.list_profiles(include_hidden=True))

        if all_profiles_count == 0:
            self.show_empty_onboarding()
        elif len(profiles) == 0:
            self.show_all_hidden_notice()
        else:
            self.show_profiles_grid(profiles)

    def show_empty_onboarding(self):
        """Display friendly onboarding when no profiles exist yet."""
        box = QFrame(self.content_widget)
        box.setStyleSheet("""
            background-color: #12151D;
            border: 1px dashed #283042;
            border-radius: 14px;
            padding: 30px;
        """)
        layout = QVBoxLayout(box)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("🚀", box)
        icon_lbl.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to YourBrowser!", box)
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(
            "Each profile has completely isolated cookies, browsing history, tabs, and bookmarks.\n"
            "Create your first profile to begin browsing safely.",
            box
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.4;")
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)

        create_btn = QPushButton("Create Your First Profile", box)
        create_btn.setFixedHeight(40)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5500;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 14px;
                border-radius: 8px;
                padding: 0 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF661A;
            }
        """)
        create_btn.clicked.connect(self.open_create_profile_dialog)
        layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(box)

    def show_all_hidden_notice(self):
        """Display notice when all existing profiles are currently hidden."""
        box = QFrame(self.content_widget)
        box.setStyleSheet("background-color: #12151D; border-radius: 12px; padding: 24px;")
        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon_lbl = QLabel("🕵️", box)
        icon_lbl.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("All your profiles are currently hidden.", box)
        lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("Press Ctrl+H to reveal hidden profiles, or create a new one.", box)
        sub_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(sub_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(box)

    def show_profiles_grid(self, profiles):
        """Render grid of profile cards."""
        grid_container = QWidget(self.content_widget)
        grid = QGridLayout(grid_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(18)

        cols = 3
        for idx, p in enumerate(profiles):
            row = idx // cols
            col = idx % cols
            card = ProfileCard(p, on_select=self.select_profile, on_delete=self.delete_profile, parent=grid_container)
            grid.addWidget(card, row, col)

        self.content_layout.addWidget(grid_container)
        self.content_layout.addStretch()

    def open_create_profile_dialog(self):
        dialog = CreateProfileDialog(self.profile_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.created_profile:
            self.refresh_profiles()
            # If user just created their first or new profile, ask if they want to launch it right away
            self.select_profile(dialog.created_profile)

    def select_profile(self, profile: Dict[str, Any]):
        """Authenticate password (if required) and launch browser window for profile."""
        profile_id = profile.get("id")
        profile_name = profile.get("name", "Profile")

        if profile.get("has_password", False):
            pwd_dialog = ProfilePasswordDialog(profile_name, profile_id, self.profile_manager, self)
            if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
                return

        self.launch_browser_for_profile(profile)

    def delete_profile(self, profile: Dict[str, Any]):
        """Confirm and delete profile."""
        name = profile.get("name", "Profile")
        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete profile '{name}'?\nAll browsing history and saved tabs will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.profile_manager.delete_profile(profile.get("id"))
            self.refresh_profiles()

    def launch_browser_for_profile(self, profile: Dict[str, Any]):
        """Launch YourBrowserWindow bound to this profile."""
        from src.ui.browser_window import YourBrowserWindow

        profile_id = profile.get("id")
        self.profile_manager.update_last_active(profile_id)

        # Close existing active browser window if any
        if self.active_browser_window:
            try:
                self.active_browser_window.close()
            except Exception:
                pass

        # Create window bound to this profile
        url = self.initial_url or "https://search.brave.com"
        self.active_browser_window = YourBrowserWindow(
            initial_url=url,
            profile_data=profile,
            dashboard_window=self,
            profile_manager=self.profile_manager
        )
        self.active_browser_window.show()
        self.hide()

    def return_to_dashboard(self):
        """Called by browser window when user clicks Dashboard button."""
        self.refresh_profiles()
        self.show()
        self.activateWindow()
        self.raise_()
