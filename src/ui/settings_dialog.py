"""
Settings Dialog Component - Brave-Style Obsidian Settings Hub
Comprehensive settings panel featuring category sidebar (Shields & Privacy,
Appearance & Customization, Search Engines, Extensions, Clear Data).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QCheckBox, QPushButton, QMessageBox, QGroupBox,
    QFormLayout, QListWidget, QListWidgetItem, QStackedWidget,
    QScrollArea, QWidget, QFrame, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon

from src.core.browser_data import SettingsManager
from src.core.extension_manager import ExtensionManager
from src.resources.icons import create_svg_icon
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, rounded_input
)


class SettingsDialog(QDialog):
    """Multi-category Brave Settings Hub."""

    settings_updated = pyqtSignal()

    def __init__(self, settings_manager: SettingsManager, extension_manager: ExtensionManager = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - YourBrowser")
        self.resize(860, 580)
        self.settings_manager = settings_manager
        self.extension_manager = extension_manager or ExtensionManager(settings_manager=self.settings_manager)

        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: 700;
                font-size: 13.5px;
                color: #FFFFFF;
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.MD};
                margin-top: 14px;
                padding-top: 20px;
                background-color: {Colors.SURFACE_1};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: {Colors.ACCENT_CYAN};
            }}
            QCheckBox {{
                color: #CBD5E1;
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
            QCheckBox::indicator:checked {{
                background-color: {Colors.ACCENT_ORANGE};
                border-color: {Colors.ACCENT_ORANGE};
                image: url(/mnt/storage/aplikasi/yourbrowser/assets/icons/ui/check_white.png);
            }}
            QComboBox {{
                background-color: {Colors.SURFACE_2};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.SM};
                padding: 6px 12px;
                color: #FFFFFF;
                font-size: 13px;
                min-height: 32px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.SURFACE_OVERLAY};
                color: #FFFFFF;
                selection-background-color: {Colors.SURFACE_3};
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(create_svg_icon("settings", Colors.ACCENT_ORANGE, 24).pixmap(24, 24))
        header.addWidget(icon_lbl)
        title_lbl = QLabel("Brave Settings Hub", self)
        title_lbl.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 800; color: #FFFFFF;")
        header.addWidget(title_lbl)
        header.addStretch()
        main_layout.addLayout(header)

        # Body: Sidebar + Stacked content
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Sidebar navigation
        self.nav_list = QListWidget(self)
        self.nav_list.setFixedWidth(200)
        self.nav_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Colors.SURFACE_1};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.MD};
                padding: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: {Radii.SM};
                color: {Colors.TEXT_SECONDARY};
                font-weight: 600;
                font-size: 13px;
                margin-bottom: 3px;
            }}
            QListWidget::item:selected {{
                background: {Gradients.SURFACE_CARD_SELECTED};
                color: #FFFFFF;
                border-left: 3px solid {Colors.ACCENT_ORANGE};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {Colors.SURFACE_2};
                color: #FFFFFF;
            }}
        """)

        categories = [
            ("shield", "Shields & Privacy", 0),
            ("palette", "Appearance", 1),
            ("search", "Search Engines", 2),
            ("extension", "Extensions", 3),
            ("trash", "Clear Data", 4),
        ]
        for icon_name, label, _ in categories:
            item = QListWidgetItem(label)
            item.setIcon(create_svg_icon(icon_name, "#94A3B8", 16))
            self.nav_list.addItem(item)
        self.nav_list.setIconSize(QSize(18, 18))

        self.nav_list.currentRowChanged.connect(self._on_category_changed)
        body_layout.addWidget(self.nav_list)

        # Pages container
        self.pages = QStackedWidget(self)
        self.pages.addWidget(self._build_shields_page())
        self.pages.addWidget(self._build_appearance_page())
        self.pages.addWidget(self._build_search_page())
        self.pages.addWidget(self._build_extensions_page())
        self.pages.addWidget(self._build_clear_data_page())
        body_layout.addWidget(self.pages, stretch=1)

        main_layout.addLayout(body_layout, stretch=1)

        # Bottom buttons
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setStyleSheet(pill_button_secondary(height=34, font_size="12px"))
        cancel_btn.clicked.connect(self.reject)
        bottom_bar.addWidget(cancel_btn)

        save_btn = QPushButton("Save & Apply", self)
        save_btn.setStyleSheet(pill_button_primary(height=34, font_size="12px"))
        save_btn.clicked.connect(self._save_settings)
        bottom_bar.addWidget(save_btn)

        main_layout.addLayout(bottom_bar)
        self.nav_list.setCurrentRow(0)

    def _on_category_changed(self, row: int):
        self.pages.setCurrentIndex(row)

    # -------------------------------------------------------------
    # 1. Shields & Privacy Page
    # -------------------------------------------------------------
    def _build_shields_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        grp = QGroupBox("Brave Shields & Aggressive Protection", page)
        form = QFormLayout(grp)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(14)

        # Trackers & Ads Blocking
        self.shield_mode_combo = QComboBox(grp)
        self.shield_mode_combo.addItems(["Aggressive (Block ads, popups & trackers)", "Standard", "Off"])
        current_mode = self.settings_manager.get("shields_ad_mode", "aggressive")
        mode_idx = 0 if current_mode == "aggressive" else (1 if current_mode == "standard" else 2)
        self.shield_mode_combo.setCurrentIndex(mode_idx)
        form.addRow("Trackers & Ads Blocking:", self.shield_mode_combo)

        # Fingerprinting
        self.cb_fingerprint = QCheckBox("Block fingerprinting attempts (Canvas & Audio spoofing)", grp)
        self.cb_fingerprint.setChecked(self.settings_manager.get("block_fingerprinting", True))
        form.addRow("", self.cb_fingerprint)

        # Social Media Trackers
        self.cb_social = QCheckBox("Block social media tracking cookies & widgets (Facebook, X, TikTok)", grp)
        self.cb_social.setChecked(self.settings_manager.get("block_social_trackers", True))
        form.addRow("", self.cb_social)

        # Force HTTPS
        self.cb_https = QCheckBox("Upgrade connections to HTTPS (Force HTTPS)", grp)
        self.cb_https.setChecked(self.settings_manager.get("force_https", True))
        form.addRow("", self.cb_https)

        # Block Popups
        self.cb_popups = QCheckBox("Neutralize window.open popups & stream click traps", grp)
        self.cb_popups.setChecked(self.settings_manager.get("block_popups", True))
        form.addRow("", self.cb_popups)

        # Cookie Policy
        self.cookie_combo = QComboBox(grp)
        self.cookie_combo.addItems(["Block cross-site tracking cookies (Recommended)", "Allow all cookies", "Block all cookies"])
        policy = self.settings_manager.get("cookie_policy", "block_third_party")
        c_idx = 0 if policy == "block_third_party" else (1 if policy == "allow_all" else 2)
        self.cookie_combo.setCurrentIndex(c_idx)
        form.addRow("Cookie Policy:", self.cookie_combo)

        layout.addWidget(grp)
        layout.addStretch()
        return page

    # -------------------------------------------------------------
    # 2. Appearance & Customization Page
    # -------------------------------------------------------------
    def _build_appearance_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        grp_theme = QGroupBox("Theme & Colors", page)
        form_theme = QFormLayout(grp_theme)
        form_theme.setContentsMargins(16, 16, 16, 16)
        form_theme.setSpacing(14)

        # Theme Mode
        self.theme_combo = QComboBox(grp_theme)
        self.theme_combo.addItems(["Brave Obsidian Dark (Default)", "Cyber Cyan Dark", "Midnight OLED Black", "Crisp Clean Light"])
        t_mode = self.settings_manager.get("theme_mode", "brave_dark")
        t_map = {"brave_dark": 0, "cyber_dark": 1, "midnight": 2, "light": 3}
        self.theme_combo.setCurrentIndex(t_map.get(t_mode, 0))
        form_theme.addRow("Theme Mode:", self.theme_combo)

        # Accent Color
        self.accent_combo = QComboBox(grp_theme)
        self.accent_combo.addItems(["Brave Flame (#FF5500)", "Cyber Cyan (#06B6D4)", "Emerald Glow (#10B981)", "Electric Purple (#A855F7)"])
        a_color = self.settings_manager.get("accent_color", "orange")
        a_map = {"orange": 0, "cyan": 1, "emerald": 2, "purple": 3}
        self.accent_combo.setCurrentIndex(a_map.get(a_color, 0))
        form_theme.addRow("Accent Color:", self.accent_combo)

        layout.addWidget(grp_theme)

        # Toolbar & Controls Group
        grp_tb = QGroupBox("Toolbar & Navigation Controls", page)
        form_tb = QFormLayout(grp_tb)
        form_tb.setContentsMargins(16, 16, 16, 16)
        form_tb.setSpacing(14)

        self.cb_home_btn = QCheckBox("Show Home button on toolbar", grp_tb)
        self.cb_home_btn.setChecked(self.settings_manager.get("show_home_button", True))
        form_tb.addRow("", self.cb_home_btn)

        self.cb_bmarks_bar = QCheckBox("Always show Bookmarks Bar (Ctrl+Shift+B)", grp_tb)
        self.cb_bmarks_bar.setChecked(self.settings_manager.get("show_bookmarks_bar", False))
        form_tb.addRow("", self.cb_bmarks_bar)

        self.cb_shields_lion = QCheckBox("Show Brave Shields Lion button with blocked ad counter", grp_tb)
        self.cb_shields_lion.setChecked(self.settings_manager.get("show_shields_lion", True))
        form_tb.addRow("", self.cb_shields_lion)

        self.homepage_input = QLineEdit(grp_tb)
        self.homepage_input.setStyleSheet(rounded_input(height=34, radius=Radii.SM))
        self.homepage_input.setText(self.settings_manager.get("homepage", "https://search.brave.com"))
        form_tb.addRow("Homepage URL:", self.homepage_input)

        self.newtab_input = QLineEdit(grp_tb)
        self.newtab_input.setStyleSheet(rounded_input(height=34, radius=Radii.SM))
        self.newtab_input.setText(self.settings_manager.get("new_tab_url", "https://search.brave.com"))
        form_tb.addRow("New Tab Page URL:", self.newtab_input)

        layout.addWidget(grp_tb)
        layout.addStretch()
        return page

    # -------------------------------------------------------------
    # 3. Search Engine Page
    # -------------------------------------------------------------
    def _build_search_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        grp = QGroupBox("Search Engine Preferences", page)
        form = QFormLayout(grp)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(14)

        self.search_combo = QComboBox(grp)
        self.search_combo.addItems(["Brave Search (Recommended)", "DuckDuckGo", "Google", "Bing", "Ecosia", "Qwant"])
        engine = self.settings_manager.get("search_engine", "brave")
        e_map = {"brave": 0, "duckduckgo": 1, "google": 2, "bing": 3, "ecosia": 4, "qwant": 5}
        self.search_combo.setCurrentIndex(e_map.get(engine, 0))
        form.addRow("Default Search Engine:", self.search_combo)

        info_lbl = QLabel("Omnibox automatically routes search queries through your chosen engine.", grp)
        info_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px;")
        form.addRow("", info_lbl)

        layout.addWidget(grp)
        layout.addStretch()
        return page

    # -------------------------------------------------------------
    # 4. Extensions Page
    # -------------------------------------------------------------
    def _build_extensions_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        desc = QLabel("Installed Chromium WebExtensions (Manifest V2/V3):", page)
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 600;")
        top_row.addWidget(desc)
        top_row.addStretch()

        load_btn = QPushButton("📁 Load Unpacked...", page)
        load_btn.setStyleSheet(pill_button_primary(height=30, font_size="11.5px"))
        load_btn.clicked.connect(self._on_load_unpacked_clicked)
        top_row.addWidget(load_btn)
        layout.addLayout(top_row)

        scroll = QScrollArea(page)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.ext_container = QWidget()
        self.ext_container.setStyleSheet("background: transparent;")
        self.ext_layout = QVBoxLayout(self.ext_container)
        self.ext_layout.setContentsMargins(0, 0, 0, 0)
        self.ext_layout.setSpacing(10)
        scroll.setWidget(self.ext_container)
        layout.addWidget(scroll, stretch=1)

        self._refresh_extensions_tab()
        return page

    def _refresh_extensions_tab(self):
        while self.ext_layout.count() > 0:
            it = self.ext_layout.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        exts = self.extension_manager.get_all_extensions()
        if not exts:
            lbl = QLabel("No extensions currently installed.", self.ext_container)
            lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; padding: 30px;")
            self.ext_layout.addWidget(lbl)
        else:
            for ext in exts:
                card = QFrame(self.ext_container)
                card.setStyleSheet(f"""
                    QFrame {{
                        background: {Colors.SURFACE_1};
                        border: 1px solid {Colors.BORDER_DEFAULT};
                        border-radius: {Radii.SM};
                        padding: 10px 14px;
                    }}
                """)
                c_layout = QHBoxLayout(card)
                c_layout.setContentsMargins(4, 4, 4, 4)

                name_lbl = QLabel(f"<b>{ext.name}</b> <span style='color:{Colors.TEXT_MUTED}; font-size:11px;'>v{ext.version}</span>", card)
                c_layout.addWidget(name_lbl)
                c_layout.addStretch()

                cb = QCheckBox("Active", card)
                cb.setChecked(self.extension_manager.is_extension_enabled(ext.id))
                cb.toggled.connect(lambda chk, eid=ext.id: self.extension_manager.set_extension_enabled(eid, chk))
                c_layout.addWidget(cb)

                self.ext_layout.addWidget(card)

        self.ext_layout.addStretch()

    def _on_load_unpacked_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Unpacked Extension Folder (Containing manifest.json)")
        if folder:
            try:
                ext = self.extension_manager.install_unpacked_extension(folder)
                QMessageBox.information(self, "Success", f"Extension {ext.name} installed successfully!")
                self._refresh_extensions_tab()
            except Exception as e:
                QMessageBox.critical(self, "Installation Error", f"Failed to install extension:\n{e}")

    # -------------------------------------------------------------
    # 5. Clear Browsing Data Page
    # -------------------------------------------------------------
    def _build_clear_data_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        grp = QGroupBox("Clear Browsing Data & Privacy Wipe", page)
        vbox = QVBoxLayout(grp)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(14)

        self.cb_clear_history = QCheckBox("Browsing History (URLs and site records)", grp)
        self.cb_clear_history.setChecked(True)
        vbox.addWidget(self.cb_clear_history)

        self.cb_clear_cache = QCheckBox("Cached Web Pages, Images & Storage Files", grp)
        self.cb_clear_cache.setChecked(True)
        vbox.addWidget(self.cb_clear_cache)

        self.cb_clear_tabs = QCheckBox("Saved Sesi Tabs (Reset open tab state)", grp)
        vbox.addWidget(self.cb_clear_tabs)

        wipe_btn = QPushButton("Clear Selected Data Now", grp)
        wipe_btn.setStyleSheet(pill_button_primary(
            gradient=Gradients.DANGER_CRIMSON,
            gradient_hover=Gradients.DANGER_CRIMSON_HOVER,
            gradient_pressed=Gradients.DANGER_CRIMSON,
            height=36,
            font_size="13px"
        ))
        wipe_btn.clicked.connect(self._on_wipe_data)
        vbox.addWidget(wipe_btn)

        layout.addWidget(grp)
        layout.addStretch()
        return page

    def _on_wipe_data(self):
        reply = QMessageBox.question(
            self, "Confirm Data Clearance",
            "Are you sure you want to clear the selected browser data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from src.core.browser_data import HistoryManager
            hm = HistoryManager(base_dir=self.settings_manager.base_dir)
            if self.cb_clear_history.isChecked():
                hm.clear()
            QMessageBox.information(self, "Cleared", "Selected browsing data has been successfully cleared.")

    # -------------------------------------------------------------
    # Save & Apply
    # -------------------------------------------------------------
    def _save_settings(self):
        # 1. Shields
        modes = ["aggressive", "standard", "off"]
        self.settings_manager.set("shields_ad_mode", modes[self.shield_mode_combo.currentIndex()])
        self.settings_manager.set("block_fingerprinting", self.cb_fingerprint.isChecked())
        self.settings_manager.set("block_social_trackers", self.cb_social.isChecked())
        self.settings_manager.set("force_https", self.cb_https.isChecked())
        self.settings_manager.set("block_popups", self.cb_popups.isChecked())
        c_policies = ["block_third_party", "allow_all", "block_all"]
        self.settings_manager.set("cookie_policy", c_policies[self.cookie_combo.currentIndex()])

        # 2. Appearance
        themes = ["brave_dark", "cyber_dark", "midnight", "light"]
        self.settings_manager.set("theme_mode", themes[self.theme_combo.currentIndex()])
        accents = ["orange", "cyan", "emerald", "purple"]
        self.settings_manager.set("accent_color", accents[self.accent_combo.currentIndex()])
        self.settings_manager.set("show_home_button", self.cb_home_btn.isChecked())
        self.settings_manager.set("show_bookmarks_bar", self.cb_bmarks_bar.isChecked())
        self.settings_manager.set("show_shields_lion", self.cb_shields_lion.isChecked())
        self.settings_manager.set("homepage", self.homepage_input.text().strip() or "https://search.brave.com")
        self.settings_manager.set("new_tab_url", self.newtab_input.text().strip() or "https://search.brave.com")

        # 3. Search Engine
        engines = ["brave", "duckduckgo", "google", "bing", "ecosia", "qwant"]
        self.settings_manager.set("search_engine", engines[self.search_combo.currentIndex()])

        self.settings_updated.emit()
        self.accept()
