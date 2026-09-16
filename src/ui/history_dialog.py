"""
History Dialog Component
Obsidian Dark modal dialog for searching, viewing, and clearing browsing history.
"""

import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize

from src.core.browser_data import HistoryManager
from src.resources.icons import create_svg_icon


class HistoryDialog(QDialog):
    """Browsing history viewer and manager."""

    open_url_requested = pyqtSignal(str)
    open_new_tab_requested = pyqtSignal(str)

    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browsing History - YourBrowser")
        self.resize(750, 520)
        self.history_manager = history_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header bar
        header_layout = QHBoxLayout()
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("history", "#FF5500", 22).pixmap(22, 22))
        header_layout.addWidget(header_icon)

        title_lbl = QLabel("Browsing History", self)
        title_lbl.setStyleSheet("font-size: 17px; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        clear_all_btn = QPushButton("Clear All History", self)
        clear_all_btn.setProperty("class", "dialog-btn-danger")
        clear_all_btn.setIcon(create_svg_icon("trash", "#FECACA", 14))
        clear_all_btn.clicked.connect(self._on_clear_all)
        header_layout.addWidget(clear_all_btn)

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit(self)
        self.search_input.setProperty("class", "dialog-search")
        self.search_input.setPlaceholderText("Search history by title or URL...")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # History list widget
        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget, stretch=1)

        # Action bar at bottom
        action_layout = QHBoxLayout()
        self.status_lbl = QLabel(self)
        self.status_lbl.setStyleSheet("color: #64748B; font-size: 12px;")
        action_layout.addWidget(self.status_lbl)
        action_layout.addStretch()

        delete_btn = QPushButton("Delete Selected", self)
        delete_btn.setProperty("class", "dialog-btn-secondary")
        delete_btn.clicked.connect(self._on_delete_selected)
        action_layout.addWidget(delete_btn)

        open_tab_btn = QPushButton("Open in New Tab", self)
        open_tab_btn.setProperty("class", "dialog-btn-secondary")
        open_tab_btn.clicked.connect(self._on_open_in_new_tab)
        action_layout.addWidget(open_tab_btn)

        open_btn = QPushButton("Open", self)
        open_btn.setProperty("class", "dialog-btn-primary")
        open_btn.clicked.connect(self._on_open)
        action_layout.addWidget(open_btn)

        layout.addLayout(action_layout)

        self._populate_list(self.history_manager.get_recent(200))

    def _populate_list(self, entries):
        self.list_widget.clear()
        for item in entries:
            ts = item.get("timestamp", 0)
            time_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else ""
            title = item.get("title") or item.get("url") or "Untitled"
            url = item.get("url", "")

            widget_item = QListWidgetItem(f"[{time_str}]  {title}\n  ↳ {url}")
            widget_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(widget_item)

        self.status_lbl.setText(f"{len(entries)} items shown")

    def _on_search_changed(self, text: str):
        results = self.history_manager.search(text, limit=200)
        self._populate_list(results)

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

    def _on_open_in_new_tab(self):
        data = self._get_selected_item_data()
        if data and data.get("url"):
            self.open_new_tab_requested.emit(data["url"])
            self.accept()

    def _on_item_double_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and data.get("url"):
            self.open_url_requested.emit(data["url"])
            self.accept()

    def _on_delete_selected(self):
        data = self._get_selected_item_data()
        if data and data.get("id"):
            self.history_manager.remove_by_id(data["id"])
            # Refresh current view
            self._on_search_changed(self.search_input.text())

    def _on_clear_all(self):
        reply = QMessageBox.question(
            self, "Confirm Clear History",
            "Are you sure you want to permanently clear all browsing history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear()
            self.list_widget.clear()
            self.status_lbl.setText("History cleared")
