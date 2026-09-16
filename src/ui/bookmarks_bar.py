"""
Bookmarks Bar Component
Horizontal quick-access bookmarks toolbar positioned below the main navigation bar.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QMenu, QScrollArea, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QAction

from src.core.browser_data import BookmarkManager
from src.resources.icons import create_svg_icon


class BookmarksBar(QWidget):
    """Bar widget displaying quick-access bookmark buttons."""

    open_url_requested = pyqtSignal(str)
    open_new_tab_requested = pyqtSignal(str)

    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.setObjectName("bookmarks_bar")
        self.bookmark_manager = bookmark_manager

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(8, 2, 8, 2)
        self.main_layout.setSpacing(6)

        # Scroll area in case user has many bookmarks
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.container_widget = QWidget(self.scroll_area)
        self.container_widget.setStyleSheet("background: transparent;")
        self.items_layout = QHBoxLayout(self.container_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(4)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.container_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.refresh_bookmarks()

    def refresh_bookmarks(self):
        """Clears and rebuilds the bookmark buttons from the BookmarkManager."""
        # Clear existing buttons
        while self.items_layout.count() > 0:
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        bookmarks = self.bookmark_manager.get_all()
        for bm in bookmarks:
            btn = QPushButton(self.container_widget)
            btn.setProperty("class", "bookmark-bar-item")
            title = bm.get("title") or bm.get("url") or "Bookmark"
            display_title = (title[:22] + "…") if len(title) > 22 else title
            btn.setText(display_title)
            btn.setToolTip(f"{title}\n{bm.get('url')}")
            btn.setIcon(create_svg_icon("star", "#F59E0B", 14))
            btn.setIconSize(QSize(14, 14))

            url = bm.get("url", "")
            bm_id = bm.get("id", "")

            # Left-click opens URL
            btn.clicked.connect(lambda checked=False, target_url=url: self.open_url_requested.emit(target_url))

            # Right-click context menu
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, target_url=url, target_id=bm_id, target_btn=btn: self._show_item_context_menu(
                    target_btn.mapToGlobal(pos), target_url, target_id
                )
            )

            self.items_layout.addWidget(btn)

        self.items_layout.addStretch()

    def _show_item_context_menu(self, global_pos, url: str, bookmark_id: str):
        menu = QMenu(self)

        open_act = menu.addAction("Open")
        open_act.triggered.connect(lambda: self.open_url_requested.emit(url))

        open_new_act = menu.addAction("Open in New Tab")
        open_new_act.triggered.connect(lambda: self.open_new_tab_requested.emit(url))

        menu.addSeparator()

        del_act = menu.addAction("Delete Bookmark")
        del_act.triggered.connect(lambda: self._delete_bookmark(bookmark_id))

        menu.exec(global_pos)

    def _delete_bookmark(self, bookmark_id: str):
        self.bookmark_manager.remove_by_id(bookmark_id)
        self.refresh_bookmarks()
