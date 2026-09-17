"""
Bookmarks Manager Dialog Component
Obsidian Dark modal dialog for searching, viewing, and managing bookmarks.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize

from src.core.browser_data import BookmarkManager
from src.resources.icons import create_svg_icon
from src.resources.style import BRAVE_THEME_QSS
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary, rounded_input
)


class BookmarksDialog(QDialog):
    """Full bookmark manager dialog."""

    open_url_requested = pyqtSignal(str)
    open_new_tab_requested = pyqtSignal(str)
    bookmarks_changed = pyqtSignal()

    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks Manager - YourBrowser")
        self.resize(720, 480)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Gradients.SURFACE_DIALOG};
                color: {Colors.TEXT_PRIMARY};
            }}
            QListWidget {{
                background-color: {Colors.SURFACE_1};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.MD};
                color: {Colors.TEXT_PRIMARY};
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: {Radii.SM};
                margin-bottom: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {Colors.SURFACE_3};
                color: {Colors.ACCENT_CYAN};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {Colors.SURFACE_2};
            }}
        """)
        self.bookmark_manager = bookmark_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("star", Colors.ACCENT_AMBER, 22).pixmap(22, 22))
        header_layout.addWidget(header_icon)

        title_lbl = QLabel("Bookmarks Manager", self)
        title_lbl.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit(self)
        self.search_input.setStyleSheet(rounded_input(height=38, radius=Radii.PILL))
        self.search_input.setPlaceholderText("Search bookmarks by title or URL...")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # List widget
        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget, stretch=1)

        # Action bar
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        self.count_lbl = QLabel(self)
        self.count_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.SIZE_SMALL};")
        action_layout.addWidget(self.count_lbl)
        action_layout.addStretch()

        delete_btn = QPushButton("Delete", self)
        delete_btn.setStyleSheet(pill_button_primary(
            gradient=Gradients.DANGER_CRIMSON,
            gradient_hover=Gradients.DANGER_CRIMSON_HOVER,
            gradient_pressed=Gradients.DANGER_CRIMSON,
            height=34,
            font_size="12px"
        ))
        delete_btn.setIcon(create_svg_icon("trash", "#FFFFFF", 14))
        delete_btn.clicked.connect(self._on_delete)
        action_layout.addWidget(delete_btn)

        open_tab_btn = QPushButton("Open in New Tab", self)
        open_tab_btn.setStyleSheet(pill_button_secondary(height=34, font_size="12px"))
        open_tab_btn.clicked.connect(self._on_open_new_tab)
        action_layout.addWidget(open_tab_btn)

        open_btn = QPushButton("Open", self)
        open_btn.setStyleSheet(pill_button_primary(height=34, font_size="12px"))
        open_btn.clicked.connect(self._on_open)
        action_layout.addWidget(open_btn)

        layout.addLayout(action_layout)

        self._populate_list(self.bookmark_manager.get_all())

    def _populate_list(self, bookmarks):
        self.list_widget.clear()
        star_icon = create_svg_icon("star", "#F59E0B", 16)
        for bm in bookmarks:
            title = bm.get("title") or bm.get("url") or "Untitled Bookmark"
            url = bm.get("url", "")
            item = QListWidgetItem(f"{title}\n{url}")
            item.setIcon(star_icon)
            item.setData(Qt.ItemDataRole.UserRole, bm)
            self.list_widget.addItem(item)

        self.count_lbl.setText(f"{len(bookmarks)} bookmarks")

    def _on_search_changed(self, text: str):
        q = text.strip().lower()
        all_bm = self.bookmark_manager.get_all()
        if not q:
            self._populate_list(all_bm)
            return

        filtered = [
            bm for bm in all_bm
            if q in bm.get("title", "").lower() or q in bm.get("url", "").lower()
        ]
        self._populate_list(filtered)

    def _get_selected_item_data(self):
        current = self.list_widget.currentItem()
        if current:
            return current.data(Qt.ItemDataRole.UserRole)
        return None

    def _on_open(self):
        data = self._get_selected_item_data()
        if data and data.get("url"):
            self.open_url_requested.emit(data["url"])
            self.accept()

    def _on_open_new_tab(self):
        data = self._get_selected_item_data()
        if data and data.get("url"):
            self.open_new_tab_requested.emit(data["url"])
            self.accept()

    def _on_item_double_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and data.get("url"):
            self.open_url_requested.emit(data["url"])
            self.accept()

    def _on_delete(self):
        data = self._get_selected_item_data()
        if data and data.get("id"):
            self.bookmark_manager.remove_by_id(data["id"])
            self.bookmarks_changed.emit()
            self._on_search_changed(self.search_input.text())
