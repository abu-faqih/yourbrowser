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
from src.resources.design_system import (
    Colors, Gradients, Radii, Typography,
    pill_button_primary, pill_button_secondary
)


class DownloadItemWidget(QWidget):
    """Custom widget rendering a single download entry in the list."""

    def __init__(self, tracker: DownloadTracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top row: icon + filename + status + buttons
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(create_svg_icon("download", Colors.ACCENT_CYAN, 18).pixmap(18, 18))
        top_row.addWidget(icon_lbl)

        self.name_lbl = QLabel(tracker.filename, self)
        self.name_lbl.setStyleSheet(f"font-weight: 600; color: #FFFFFF; font-size: 13.5px;")
        top_row.addWidget(self.name_lbl, stretch=1)

        self.status_lbl = QLabel(self)
        self.status_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        top_row.addWidget(self.status_lbl)

        # Action buttons (Pills)
        self.open_file_btn = QPushButton("Open File", self)
        self.open_file_btn.setStyleSheet(pill_button_secondary(height=28, font_size="11.5px"))
        self.open_file_btn.clicked.connect(self._open_file)
        top_row.addWidget(self.open_file_btn)

        self.open_dir_btn = QPushButton("Open Folder", self)
        self.open_dir_btn.setStyleSheet(pill_button_secondary(height=28, font_size="11.5px"))
        self.open_dir_btn.clicked.connect(self._open_folder)
        top_row.addWidget(self.open_dir_btn)

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setStyleSheet(pill_button_primary(
            gradient=Gradients.DANGER_CRIMSON,
            gradient_hover=Gradients.DANGER_CRIMSON_HOVER,
            gradient_pressed=Gradients.DANGER_CRIMSON,
            height=28,
            font_size="11.5px"
        ))
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
                background-color: #181D2C;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #FF2A54);
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


from src.resources.style import BRAVE_THEME_QSS


class DownloadsDialog(QDialog):
    """Downloads queue and history dialog."""

    def __init__(self, download_manager: DownloadManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads - YourBrowser")
        self.resize(750, 480)
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
                background-color: {Colors.SURFACE_2};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radii.MD};
                margin-bottom: 6px;
                padding: 4px;
            }}
            QListWidget::item:hover {{
                border-color: {Colors.BORDER_DEFAULT};
            }}
        """)
        self.download_manager = download_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_icon = QLabel(self)
        header_icon.setPixmap(create_svg_icon("download", Colors.ACCENT_ORANGE, 22).pixmap(22, 22))
        header_layout.addWidget(header_icon)

        title_lbl = QLabel("Downloads", self)
        title_lbl.setStyleSheet(f"font-size: {Typography.SIZE_SUBTITLE}; font-weight: 700; color: #FFFFFF;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        open_folder_btn = QPushButton("Open Downloads Folder", self)
        open_folder_btn.setStyleSheet(pill_button_secondary(height=34, font_size="12px"))
        open_folder_btn.setIcon(create_svg_icon("folder", "#CBD5E1", 14))
        open_folder_btn.clicked.connect(self._open_downloads_dir)
        header_layout.addWidget(open_folder_btn)

        clear_btn = QPushButton("Clear Finished", self)
        clear_btn.setStyleSheet(pill_button_secondary(height=34, font_size="12px"))
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
