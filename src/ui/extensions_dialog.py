"""
YourBrowser UI - Extensions Manager Dialog
Brave Obsidian Dark modal for managing Chromium WebExtensions (Manifest V2/V3),
installing unpacked extensions, and toggling content script injection.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from src.core.extension_manager import ExtensionManager, BrowserExtension
from src.resources.icons import create_svg_icon
from src.resources.style import BRAVE_THEME_QSS
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, pill_badge
)


class ExtensionCard(QFrame):
    """Card widget representing a single installed extension."""
    status_changed = pyqtSignal(str, bool)
    removed = pyqtSignal(str)

    def __init__(self, extension: BrowserExtension, is_enabled: bool, parent=None):
        super().__init__(parent)
        self.extension = extension
        self.is_enabled = is_enabled
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {Gradients.SURFACE_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.MD};
                padding: 16px;
            }}
            QFrame:hover {{
                border-color: {Colors.BORDER_HOVER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header: Icon + Name + Version + Toggle
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(create_svg_icon("extension" if self.extension.is_builtin else "cube", "#38BDF8", 22).pixmap(22, 22))
        top_row.addWidget(icon_lbl)

        name_lbl = QLabel(self.extension.name, self)
        name_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #FFFFFF;")
        top_row.addWidget(name_lbl)

        ver_lbl = QLabel(f"v{self.extension.version}", self)
        ver_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        top_row.addWidget(ver_lbl)

        if self.extension.is_builtin:
            badge = QLabel("BUILT-IN", self)
            badge.setStyleSheet(f"""
                background-color: {Colors.SURFACE_3};
                color: {Colors.ACCENT_CYAN};
                border: 1px solid {Colors.ACCENT_CYAN};
                border-radius: {Radii.PILL};
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
            """)
            top_row.addWidget(badge)

        top_row.addStretch()

        self.toggle_cb = QCheckBox("Enabled", self)
        self.toggle_cb.setChecked(self.is_enabled)
        self.toggle_cb.setStyleSheet(f"""
            QCheckBox {{
                color: #FFFFFF;
                font-weight: 600;
                font-size: 12px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                background: {Colors.SURFACE_1};
            }}
            QCheckBox::indicator:checked {{
                background: {Colors.ACCENT_ORANGE};
                border-color: {Colors.ACCENT_ORANGE};
            }}
        """)
        self.toggle_cb.toggled.connect(lambda chk: self.status_changed.emit(self.extension.id, chk))
        top_row.addWidget(self.toggle_cb)

        layout.addLayout(top_row)

        # Description
        if self.extension.description:
            desc_lbl = QLabel(self.extension.description, self)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; line-height: 1.4;")
            layout.addWidget(desc_lbl)

        # Footer info: Permissions & ID
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        id_lbl = QLabel(f"ID: {self.extension.id}  •  Manifest V{self.extension.manifest_version}", self)
        id_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        bottom_row.addWidget(id_lbl)
        bottom_row.addStretch()

        if not self.extension.is_builtin:
            remove_btn = QPushButton("Remove", self)
            remove_btn.setStyleSheet(pill_button_primary(
                gradient=Gradients.DANGER_CRIMSON,
                gradient_hover=Gradients.DANGER_CRIMSON_HOVER,
                gradient_pressed=Gradients.DANGER_CRIMSON,
                height=26,
                font_size="11px"
            ))
            remove_btn.clicked.connect(lambda: self.removed.emit(self.extension.id))
            bottom_row.addWidget(remove_btn)

        layout.addLayout(bottom_row)


class ExtensionsDialog(QDialog):
    """Management modal for all installed extensions."""
    extensions_changed = pyqtSignal()

    def __init__(self, extension_manager: ExtensionManager, parent=None):
        super().__init__(parent)
        self.extension_manager = extension_manager
        self.setWindowTitle("Extensions - YourBrowser")
        self.resize(680, 520)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # Header Bar
        header = QHBoxLayout()
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("extension", Colors.ACCENT_CYAN, 24).pixmap(24, 24))
        header.addWidget(header_icon)

        title = QLabel("Extensions", self)
        title.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 700; color: #FFFFFF;")
        header.addWidget(title)

        header.addStretch()

        load_btn = QPushButton("📁 Load Unpacked...", self)
        load_btn.setStyleSheet(pill_button_primary(height=34, font_size="12px"))
        load_btn.clicked.connect(self._on_load_unpacked)
        header.addWidget(load_btn)

        main_layout.addLayout(header)

        sub_desc = QLabel("Manage installed Chromium WebExtensions (Manifest V2 and V3).", self)
        sub_desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        main_layout.addWidget(sub_desc)

        # Scroll Area for extension list
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.container_widget = QWidget()
        self.container_widget.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.container_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        scroll.setWidget(self.container_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Close button at bottom
        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Done", self)
        close_btn.setStyleSheet(pill_button_secondary(height=34, font_size="12px"))
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        main_layout.addLayout(footer)

        self.refresh_list()

    def refresh_list(self):
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        extensions = self.extension_manager.get_all_extensions()
        if not extensions:
            empty_lbl = QLabel("No extensions installed yet.\nClick 'Load Unpacked...' to install an extension.", self)
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 13px; padding: 40px;")
            self.cards_layout.addWidget(empty_lbl)
        else:
            for ext in extensions:
                is_enabled = self.extension_manager.is_extension_enabled(ext.id)
                card = ExtensionCard(ext, is_enabled, self.container_widget)
                card.status_changed.connect(self._on_extension_status_changed)
                card.removed.connect(self._on_extension_removed)
                self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def _on_extension_status_changed(self, ext_id: str, enabled: bool):
        self.extension_manager.set_extension_enabled(ext_id, enabled)
        self.extensions_changed.emit()

    def _on_extension_removed(self, ext_id: str):
        reply = QMessageBox.question(
            self, "Remove Extension",
            f"Are you sure you want to remove extension {ext_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.extension_manager.remove_extension(ext_id)
            self.refresh_list()
            self.extensions_changed.emit()

    def _on_load_unpacked(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Unpacked Extension Folder (Containing manifest.json)")
        if folder:
            try:
                ext = self.extension_manager.install_unpacked_extension(folder)
                QMessageBox.information(self, "Success", f"Extension {ext.name} (v{ext.version}) installed successfully!")
                self.refresh_list()
                self.extensions_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Installation Error", f"Failed to install extension:\n{e}")
