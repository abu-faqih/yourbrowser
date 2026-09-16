"""
Settings Dialog Component
Obsidian Dark preferences dialog for default search engine, homepage, and privacy options.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QCheckBox, QPushButton, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

from src.core.browser_data import SettingsManager
from src.resources.icons import create_svg_icon
from src.resources.style import BRAVE_THEME_QSS
from src.resources.design_system import Colors, Radii


class SettingsDialog(QDialog):
    """Application preferences and settings modal."""

    settings_updated = pyqtSignal()

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - YourBrowser")
        self.resize(560, 420)
        self.setStyleSheet(BRAVE_THEME_QSS)
        self.settings_manager = settings_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Header
        header_layout = QHBoxLayout()
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("settings", "#FF5500", 22).pixmap(22, 22))
        header_layout.addWidget(header_icon)

        title_lbl = QLabel("Browser Settings", self)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Form Group
        form_group = QGroupBox("Search & Navigation", self)
        form_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.MD};
                margin-top: 10px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
            }}
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(14)

        # Search Engine Combo
        self.engine_combo = QComboBox(form_group)
        self.engine_combo.addItems(["Brave Search", "DuckDuckGo", "Google", "Bing"])
        self.engine_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.SURFACE_1};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.SM};
                padding: 7px 14px;
                color: #FFFFFF;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.SURFACE_OVERLAY};
                color: #FFFFFF;
                selection-background-color: {Colors.SURFACE_3};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.SM};
            }}
        """)

        current_engine = self.settings_manager.get("search_engine", "brave")
        engine_map = {"brave": 0, "duckduckgo": 1, "google": 2, "bing": 3}
        self.engine_combo.setCurrentIndex(engine_map.get(current_engine, 0))
        form_layout.addRow("Default Search Engine:", self.engine_combo)

        # Homepage Input
        self.homepage_input = QLineEdit(form_group)
        self.homepage_input.setProperty("class", "dialog-search")
        self.homepage_input.setText(self.settings_manager.get("homepage", "https://search.brave.com"))
        form_layout.addRow("Homepage URL:", self.homepage_input)

        # Show Bookmarks Bar Checkbox
        self.bookmarks_bar_cb = QCheckBox("Always show Bookmarks Bar", form_group)
        self.bookmarks_bar_cb.setChecked(self.settings_manager.get("show_bookmarks_bar", True))
        self.bookmarks_bar_cb.setStyleSheet("color: #CBD5E1; font-size: 13px;")
        form_layout.addRow("", self.bookmarks_bar_cb)

        layout.addWidget(form_group)

        # Buttons at bottom
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "dialog-btn-secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes", self)
        save_btn.setProperty("class", "dialog-btn-primary")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save_settings(self):
        engine_keys = ["brave", "duckduckgo", "google", "bing"]
        selected_idx = self.engine_combo.currentIndex()
        chosen_engine = engine_keys[selected_idx] if 0 <= selected_idx < len(engine_keys) else "brave"

        self.settings_manager.set("search_engine", chosen_engine)
        self.settings_manager.set("homepage", self.homepage_input.text().strip() or "https://search.brave.com")
        self.settings_manager.set("show_bookmarks_bar", self.bookmarks_bar_cb.isChecked())

        self.settings_updated.emit()
        self.accept()
