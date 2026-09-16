"""
Downloads Dialog Component
Obsidian Dark modal dialog for tracking and managing file downloads.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices

from src.core.download_manager import DownloadManager, DownloadTracker, DownloadItemState
from src.resources.icons import create_svg_icon


class DownloadItemWidget(QWidget):
    """Custom widget rendering a single download entry in the list."""

    def __init__(self, tracker: DownloadTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Top row: icon + filename + status + buttons
        top_row = QHBoxLayout()
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(create_svg_icon("download", "#38BDF8", 16).pixmap(16, 16))
        top_row.addWidget(icon_lbl)

        self.name_lbl = QLabel(tracker.filename, self)
        self.name_lbl.setStyleSheet("font-weight: 600; color: #FFFFFF; font-size: 13px;")
        top_row.addWidget(self.name_lbl, stretch=1)

        self.status_lbl = QLabel(self)
        self.status_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        top_row.addWidget(self.status_lbl)

        # Action buttons
        self.open_file_btn = QPushButton("Open File", self)
        self.open_file_btn.setProperty("class", "dialog-btn-secondary")
        self.open_file_btn.setFixedHeight(28)
        self.open_file_btn.clicked.connect(self._open_file)
        top_row.addWidget(self.open_file_btn)

        self.open_dir_btn = QPushButton("Open Folder", self)
        self.open_dir_btn.setProperty("class", "dialog-btn-secondary")
        self.open_dir_btn.setFixedHeight(28)
        self.open_dir_btn.clicked.connect(self._open_folder)
        top_row.addWidget(self.open_dir_btn)

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setProperty("class", "dialog-btn-danger")
        self.cancel_btn.setFixedHeight(28)
        self.cancel_btn.clicked.connect(self.tracker.cancel)
        top_row.addWidget(self.cancel_btn)

        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #1E2535;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #FF5500;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.update_ui()
        tracker.updated.connect(self.update_ui)

    def update_ui(self):
        state = self.tracker.state
        if state == DownloadItemState.IN_PROGRESS:
            pct = self.tracker.percentage
            self.progress_bar.show()
            self.progress_bar.setValue(pct)
            mb_recv = self.tracker.received_bytes / (1024 * 1024)
            mb_total = self.tracker.total_bytes / (1024 * 1024)
            self.status_lbl.setText(f"{pct}% ({mb_recv:.1f}/{mb_total:.1f} MB)")
            self.open_file_btn.setEnabled(False)
            self.cancel_btn.show()
        elif state == DownloadItemState.COMPLETED:
            self.progress_bar.hide()
            mb_total = self.tracker.total_bytes / (1024 * 1024) if self.tracker.total_bytes > 0 else 0
            self.status_lbl.setText(f"Completed ({mb_total:.1f} MB)" if mb_total > 0 else "Completed")
            self.status_lbl.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 500;")
            self.open_file_btn.setEnabled(True)
            self.cancel_btn.hide()
        elif state == DownloadItemState.CANCELLED:
            self.progress_bar.hide()
            self.status_lbl.setText("Cancelled")
            self.status_lbl.setStyleSheet("color: #EF4444; font-size: 12px;")
            self.open_file_btn.setEnabled(False)
            self.cancel_btn.hide()
        else:
            self.progress_bar.hide()
            self.status_lbl.setText("Interrupted")
            self.open_file_btn.setEnabled(False)
            self.cancel_btn.hide()

    def _open_file(self):
        if os.path.exists(self.tracker.save_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.tracker.save_path))

    def _open_folder(self):
        folder = os.path.dirname(self.tracker.save_path)
        if os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


class DownloadsDialog(QDialog):
    """Downloads queue and history dialog."""

    def __init__(self, download_manager: DownloadManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads - YourBrowser")
        self.resize(750, 480)
        self.download_manager = download_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("download", "#FF5500", 22).pixmap(22, 22))
        header_layout.addWidget(header_icon)

        title_lbl = QLabel("Downloads", self)
        title_lbl.setStyleSheet("font-size: 17px; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        open_folder_btn = QPushButton("Open Downloads Folder", self)
        open_folder_btn.setProperty("class", "dialog-btn-secondary")
        open_folder_btn.setIcon(create_svg_icon("folder", "#CBD5E1", 14))
        open_folder_btn.clicked.connect(self._open_downloads_dir)
        header_layout.addWidget(open_folder_btn)

        clear_btn = QPushButton("Clear Finished", self)
        clear_btn.setProperty("class", "dialog-btn-secondary")
        clear_btn.clicked.connect(self._clear_finished)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Downloads List
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget, stretch=1)

        self._populate_list()
        self.download_manager.download_started.connect(self._populate_list)

    def _populate_list(self):
        self.list_widget.clear()
        downloads = self.download_manager.get_all_downloads()
        for tracker in downloads:
            item = QListWidgetItem(self.list_widget)
            widget = DownloadItemWidget(tracker, self)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def _open_downloads_dir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.download_manager.download_dir))

    def _clear_finished(self):
        self.download_manager.clear_finished()
        self._populate_list()
