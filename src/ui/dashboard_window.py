"""
YourBrowser UI - Profile Dashboard Window
Ultra-Modern Brave Obsidian Dark aesthetic with unified Design System:
pill buttons, rounded cards, vibrant gradients, and isolated profile management.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QDialog, QCheckBox,
    QGridLayout, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from src.core.profile_manager import ProfileManager, DEFAULT_AVATAR_COLORS
from src.resources.style import BRAVE_THEME_QSS
from src.resources.icons import create_svg_icon, create_svg_pixmap
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, pill_badge, rounded_input
)
from src.ui.browser_window import YourBrowserWindow


class ProfilePasswordDialog(QDialog):
    """Dialog asking for profile password before unlocking."""

    def __init__(self, profile_name: str, profile_id: str, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.profile_manager = profile_manager
        self.setWindowTitle("Unlock Profile")
        self.setFixedSize(400, 250)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.LG};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title_lbl = QLabel(f"Unlock '{profile_name}'", self)
        title_lbl.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel("This profile is password-protected. Enter your password to continue:", self)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL};")
        layout.addWidget(desc_lbl)

        self.pwd_input = QLineEdit(self)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter profile password...")
        self.pwd_input.setStyleSheet(rounded_input(38, Radii.SM))
        self.pwd_input.returnPressed.connect(self.verify_and_accept)
        layout.addWidget(self.pwd_input)

        self.error_lbl = QLabel("", self)
        self.error_lbl.setStyleSheet(f"color: {Colors.STATUS_DANGER}; font-size: {Typography.SIZE_SMALL};")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setStyleSheet(pill_button_secondary(height=36, font_size="13px"))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        unlock_btn = QPushButton("Unlock", self)
        unlock_btn.setStyleSheet(pill_button_primary(height=36, font_size="13px"))
        unlock_btn.clicked.connect(self.verify_and_accept)
        btn_row.addWidget(unlock_btn)

        layout.addLayout(btn_row)

    def verify_and_accept(self):
        pwd = self.pwd_input.text()
        if not pwd:
            self.error_lbl.setText("Password cannot be empty.")
            self.error_lbl.show()
            return

        if self.profile_manager.verify_password(self.profile_id, pwd):
            self.accept()
        else:
            self.error_lbl.setText("Incorrect password. Please try again.")
            self.error_lbl.show()
            self.pwd_input.clear()
            self.pwd_input.setFocus()


class CreateProfileDialog(QDialog):
    """Dialog to create a new profile with optional password & stealth setting."""

    def __init__(self, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.created_profile: Optional[Dict[str, Any]] = None

        self.setWindowTitle("Create New Profile")
        self.setFixedSize(440, 390)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.LG};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title_lbl = QLabel("Add New Browser Profile", self)
        title_lbl.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        # Profile Name
        name_lbl = QLabel("Profile Name:", self)
        name_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: {Typography.SIZE_SMALL};")
        layout.addWidget(name_lbl)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("e.g. Work, Personal, Crypto, Stealth...")
        self.name_input.setStyleSheet(rounded_input(38, Radii.SM))
        layout.addWidget(self.name_input)

        # Password (Optional)
        pwd_lbl = QLabel("Password Protection (Optional):", self)
        pwd_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: {Typography.SIZE_SMALL}; margin-top: 4px;")
        layout.addWidget(pwd_lbl)

        self.pwd_input = QLineEdit(self)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Leave blank for no password")
        self.pwd_input.setStyleSheet(rounded_input(38, Radii.SM))
        layout.addWidget(self.pwd_input)

        # Hidden Checkbox
        self.hide_chk = QCheckBox("Hide this profile (Toggle view with Ctrl+H)", self)
        self.hide_chk.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; margin-top: 4px;")
        layout.addWidget(self.hide_chk)

        self.error_lbl = QLabel("", self)
        self.error_lbl.setStyleSheet(f"color: {Colors.STATUS_DANGER}; font-size: {Typography.SIZE_SMALL};")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setStyleSheet(pill_button_secondary(height=36))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Create Profile", self)
        save_btn.setStyleSheet(pill_button_primary(height=36))
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
    """Interactive visual card representing a single profile with pill badges & gradient button."""

    def __init__(self, profile: Dict[str, Any], on_select, on_delete, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.on_select = on_select
        self.on_delete = on_delete

        self.setObjectName("profile_card")
        self.setFixedSize(230, 250)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            #profile_card {{
                background: {Gradients.SURFACE_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.LG};
            }}
            #profile_card:hover {{
                background: {Gradients.SURFACE_CARD_HOVER};
                border: 1px solid {Colors.ACCENT_ORANGE};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar Circle
        avatar_color = profile.get("avatar_color", Colors.ACCENT_ORANGE)
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
            border: 2px solid rgba(255, 255, 255, 0.2);
        """)
        layout.addWidget(avatar_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Profile Name
        name_lbl = QLabel(profile.get("name", "Profile"), self)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(name_lbl)

        # Status Badges in Pill shape
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(6)
        badges_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if profile.get("has_password", False):
            lock_badge = QFrame(self)
            lock_badge.setStyleSheet(f"background-color: {Colors.STATUS_DANGER_BG}; border: 1px solid {Colors.STATUS_DANGER}; border-radius: 9999px; padding: 2px 8px;")
            lb_layout = QHBoxLayout(lock_badge)
            lb_layout.setContentsMargins(4, 2, 6, 2)
            lb_layout.setSpacing(4)
            lb_ico = QLabel(lock_badge)
            lb_ico.setPixmap(create_svg_pixmap("lock", "#FCA5A5", 11))
            lb_txt = QLabel("Locked", lock_badge)
            lb_txt.setStyleSheet("color: #FCA5A5; font-size: 10px; font-weight: 700;")
            lb_layout.addWidget(lb_ico)
            lb_layout.addWidget(lb_txt)
            badges_layout.addWidget(lock_badge)

        if profile.get("is_hidden", False):
            hidden_badge = QFrame(self)
            hidden_badge.setStyleSheet(f"background-color: {Colors.SURFACE_3}; border: 1px solid {Colors.ACCENT_CYAN}; border-radius: 9999px; padding: 2px 8px;")
            hb_layout = QHBoxLayout(hidden_badge)
            hb_layout.setContentsMargins(4, 2, 6, 2)
            hb_layout.setSpacing(4)
            hb_ico = QLabel(hidden_badge)
            hb_ico.setPixmap(create_svg_pixmap("eye", Colors.ACCENT_CYAN, 11))
            hb_txt = QLabel("Hidden", hidden_badge)
            hb_txt.setStyleSheet(f"color: {Colors.ACCENT_CYAN}; font-size: 10px; font-weight: 700;")
            hb_layout.addWidget(hb_ico)
            hb_layout.addWidget(hb_txt)
            badges_layout.addWidget(hidden_badge)

        layout.addLayout(badges_layout)

        # Launch Button (Pill Primary Flame)
        self.launch_btn = QPushButton("Open Profile", self)
        self.launch_btn.setStyleSheet(pill_button_primary(height=32, font_size="12px"))
        self.launch_btn.clicked.connect(lambda: self.on_select(self.profile))
        layout.addWidget(self.launch_btn)

        # Delete action button
        self.del_btn = QPushButton("Delete", self)
        self.del_btn.setFixedHeight(20)
        self.del_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_MUTED};
                font-size: 11px;
                border: none;
            }}
            QPushButton:hover {{
                color: {Colors.STATUS_DANGER};
                text-decoration: underline;
            }}
        """)
        self.del_btn.clicked.connect(lambda: self.on_delete(self.profile))
        layout.addWidget(self.del_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.pos())
            if child not in (self.del_btn, self.launch_btn):
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
        self.resize(980, 700)
        self.setStyleSheet(BRAVE_THEME_QSS)
        
        from src.resources.icons import get_app_icon, get_app_pixmap
        self.setWindowIcon(get_app_icon())

        self.setup_ui()
        self.setup_shortcuts()
        self.refresh_profiles()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(36, 32, 36, 32)
        self.main_layout.setSpacing(22)

        # Header Bar
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Logo & App Title
        from src.resources.icons import get_app_pixmap
        logo_box = QHBoxLayout()
        logo_box.setSpacing(12)
        
        logo_pixmap = get_app_pixmap(44)
        if not logo_pixmap.isNull():
            logo_img_lbl = QLabel(header_widget)
            logo_img_lbl.setPixmap(logo_pixmap)
            logo_img_lbl.setFixedSize(44, 44)
            logo_box.addWidget(logo_img_lbl)
        else:
            shield_icon = QLabel(header_widget)
            shield_icon.setPixmap(create_svg_pixmap("shield", Colors.ACCENT_ORANGE, 36))
            logo_box.addWidget(shield_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        app_title = QLabel("YourBrowser", header_widget)
        app_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;")
        sub_title = QLabel("Isolated Profiles & Vault Dashboard", header_widget)
        sub_title.setStyleSheet(f"font-size: {Typography.SIZE_SMALL}; color: {Colors.TEXT_SECONDARY};")
        title_col.addWidget(app_title)
        title_col.addWidget(sub_title)
        logo_box.addLayout(title_col)

        header_layout.addLayout(logo_box)
        header_layout.addStretch()

        # Hidden profile status badge (Pill)
        self.hidden_status_lbl = QLabel("", header_widget)
        self.hidden_status_lbl.setStyleSheet(
            pill_badge(Colors.SURFACE_3, Colors.ACCENT_CYAN, "11px") + f"border: 1px solid {Colors.ACCENT_CYAN}; padding: 6px 14px;"
        )
        self.hidden_status_lbl.hide()
        header_layout.addWidget(self.hidden_status_lbl)

        # Toggle Hidden Profiles Button (Interactive Pill Button)
        self.toggle_hidden_btn = QPushButton(" Show Hidden", header_widget)
        self.toggle_hidden_btn.setIcon(create_svg_icon("eye", "#94A3B8", 16))
        self.toggle_hidden_btn.setToolTip("Toggle visibility of hidden profiles (Ctrl+H)")
        self.toggle_hidden_btn.setStyleSheet(pill_button_secondary(height=38, font_size="13px"))
        self.toggle_hidden_btn.clicked.connect(self.toggle_hidden_profiles)
        header_layout.addWidget(self.toggle_hidden_btn)

        # Add Profile Button (Pill Primary Flame)
        self.add_profile_btn = QPushButton(" New Profile", header_widget)
        self.add_profile_btn.setIcon(create_svg_icon("plus", "#FFFFFF", 16))
        self.add_profile_btn.setStyleSheet(pill_button_primary(height=38, font_size="13px"))
        self.add_profile_btn.clicked.connect(self.open_create_profile_dialog)
        header_layout.addWidget(self.add_profile_btn)

        self.main_layout.addWidget(header_widget)

        # Divider line
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {Colors.BORDER_SUBTLE};")
        self.main_layout.addWidget(divider)

        # Scrollable Profiles Content Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 12, 0, 12)
        self.content_layout.setSpacing(18)
        self.scroll_area.setWidget(self.content_widget)

        self.main_layout.addWidget(self.scroll_area, stretch=1)

        # Footer shortcut hint
        footer_lbl = QLabel("Tip: Press Ctrl+H or click 'Show Hidden' to toggle visibility of hidden profiles", self)
        footer_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11.5px;")
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(footer_lbl)

    def setup_shortcuts(self):
        """Register keyboard shortcuts for toggling hidden profiles across the entire window."""
        self._shortcuts = []
        for seq in ["Ctrl+H", "Ctrl+h", "Ctrl+Shift+H"]:
            sc = QShortcut(QKeySequence(seq), self)
            sc.setContext(Qt.ShortcutContext.ApplicationShortcut)
            sc.activated.connect(self.toggle_hidden_profiles)
            self._shortcuts.append(sc)

    def keyPressEvent(self, event):
        """Hardware fallback key press handler for Ctrl+H."""
        if (event.modifiers() & Qt.KeyboardModifier.ControlModifier) and event.key() == Qt.Key.Key_H:
            self.toggle_hidden_profiles()
            event.accept()
            return
        super().keyPressEvent(event)

    def toggle_hidden_profiles(self):
        """Toggle viewing of hidden profiles with visual feedback."""
        self.show_hidden = not self.show_hidden
        if self.show_hidden:
            if hasattr(self, "toggle_hidden_btn"):
                self.toggle_hidden_btn.setText(" Hide Hidden")
                self.toggle_hidden_btn.setIcon(create_svg_icon("eye_off", Colors.ACCENT_CYAN, 16))
                self.toggle_hidden_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #1E293B;
                        color: {Colors.ACCENT_CYAN};
                        border: 1px solid {Colors.ACCENT_CYAN};
                        border-radius: {Radii.PILL};
                        font-weight: 700;
                        font-size: 13px;
                        padding: 0 16px;
                    }}
                    QPushButton:hover {{
                        background-color: #26354A;
                        color: #FFFFFF;
                    }}
                """)
            self.hidden_status_lbl.setText("Hidden Profiles: Visible")
            self.hidden_status_lbl.show()
        else:
            if hasattr(self, "toggle_hidden_btn"):
                self.toggle_hidden_btn.setText(" Show Hidden")
                self.toggle_hidden_btn.setIcon(create_svg_icon("eye", "#94A3B8", 16))
                self.toggle_hidden_btn.setStyleSheet(pill_button_secondary(height=38, font_size="13px"))
            self.hidden_status_lbl.hide()
        self.refresh_profiles()

    def refresh_profiles(self):
        """Clear and redraw profile cards or onboarding empty state."""
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
        box.setStyleSheet(f"""
            background: {Gradients.SURFACE_CARD};
            border: 1px dashed {Colors.BORDER_DEFAULT};
            border-radius: {Radii.LG};
            padding: 36px;
        """)
        layout = QVBoxLayout(box)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(box)
        icon_lbl.setPixmap(create_svg_pixmap("user", Colors.ACCENT_ORANGE, 48))
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to YourBrowser!", box)
        title.setStyleSheet(f"font-size: {Typography.SIZE_TITLE}; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(
            "Each profile has completely isolated cookies, browsing history, tabs, and bookmarks.\n"
            "Create your first profile to begin browsing safely.",
            box
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_BODY}; line-height: 1.5;")
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)

        create_btn = QPushButton(" Create Your First Profile", box)
        create_btn.setIcon(create_svg_icon("plus", "#FFFFFF", 16))
        create_btn.setStyleSheet(pill_button_primary(height=42, font_size="14px"))
        create_btn.clicked.connect(self.open_create_profile_dialog)
        layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(box)

    def show_all_hidden_notice(self):
        """Display notice when all existing profiles are currently hidden."""
        box = QFrame(self.content_widget)
        box.setStyleSheet(f"background: {Gradients.SURFACE_CARD}; border-radius: {Radii.LG}; padding: 30px; border: 1px solid {Colors.BORDER_DEFAULT};")
        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel(box)
        icon_lbl.setPixmap(create_svg_pixmap("eye", Colors.ACCENT_CYAN, 40))
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("All your profiles are currently hidden.", box)
        lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("Press Ctrl+H or click below to reveal hidden profiles, or create a new one.", box)
        sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(sub_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        reveal_btn = QPushButton(" Show Hidden Profiles Now (Ctrl+H)", box)
        reveal_btn.setIcon(create_svg_icon("eye", "#FFFFFF", 16))
        reveal_btn.setStyleSheet(pill_button_primary(height=40, font_size="13px"))
        reveal_btn.clicked.connect(self.toggle_hidden_profiles)
        layout.addWidget(reveal_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(box)

    def show_profiles_grid(self, profiles):
        """Render grid of profile cards."""
        grid_container = QWidget(self.content_widget)
        grid = QGridLayout(grid_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(20)

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
            # If newly created profile is hidden, automatically reveal hidden profiles so user sees it
            if dialog.created_profile.get("is_hidden", False) and not self.show_hidden:
                self.toggle_hidden_profiles()
            else:
                self.refresh_profiles()
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
        profile_id = profile.get("id")
        self.profile_manager.update_last_active(profile_id)

        if self.active_browser_window:
            try:
                self.active_browser_window.close()
            except Exception:
                pass

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
