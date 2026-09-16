"""
Find In Page Component
Floating / inline search bar widget for page text searching (Ctrl+F).
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage

from src.resources.icons import create_svg_icon
from src.resources.design_system import Colors, Gradients, Radii, Typography, rounded_input


class FindInPageWidget(QWidget):
    """Find text in active page bar styled as a modern Obsidian pill widget."""

    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("find_bar")
        self.active_view = None

        self.setStyleSheet(f"""
            QWidget#find_bar {{
                background: {Gradients.SURFACE_DIALOG};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radii.PILL};
                padding: 4px 10px;
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {Radii.PILL};
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {Colors.SURFACE_3};
                border: 1px solid {Colors.BORDER_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.SURFACE_2};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Search icon
        search_icon_lbl = QLabel(self)
        search_icon_lbl.setPixmap(create_svg_icon("find", Colors.ACCENT_CYAN, 15).pixmap(15, 15))
        layout.addWidget(search_icon_lbl)

        # Search input
        self.input_field = QLineEdit(self)
        self.input_field.setObjectName("find_input")
        self.input_field.setPlaceholderText("Find in page...")
        self.input_field.setStyleSheet(rounded_input(height=30, radius=Radii.PILL))
        self.input_field.textChanged.connect(self._on_text_changed)
        self.input_field.returnPressed.connect(self.find_next)
        layout.addWidget(self.input_field)

        # Prev button
        self.prev_btn = QPushButton(self)
        self.prev_btn.setIcon(create_svg_icon("arrow_left", Colors.TEXT_SECONDARY, 14))
        self.prev_btn.setIconSize(QSize(14, 14))
        self.prev_btn.setToolTip("Previous match (Shift+Enter)")
        self.prev_btn.setFixedSize(28, 28)
        self.prev_btn.clicked.connect(self.find_prev)
        layout.addWidget(self.prev_btn)

        # Next button
        self.next_btn = QPushButton(self)
        self.next_btn.setIcon(create_svg_icon("arrow_right", Colors.TEXT_SECONDARY, 14))
        self.next_btn.setIconSize(QSize(14, 14))
        self.next_btn.setToolTip("Next match (Enter)")
        self.next_btn.setFixedSize(28, 28)
        self.next_btn.clicked.connect(self.find_next)
        layout.addWidget(self.next_btn)

        # Close button
        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(create_svg_icon("close", Colors.TEXT_MUTED, 14))
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.setToolTip("Close find bar (Esc)")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.close_bar)
        layout.addWidget(self.close_btn)

        self.hide()

    def set_active_view(self, web_view):
        """Bind the search bar to the currently active web view."""
        self.active_view = web_view

    def open_bar(self):
        """Shows the find bar and focuses the input."""
        self.show()
        self.raise_()
        self.input_field.selectAll()
        self.input_field.setFocus()
        query = self.input_field.text()
        if query and self.active_view:
            self.active_view.findText(query)

    def close_bar(self):
        """Hides the find bar and clears text highlighting."""
        if self.active_view:
            self.active_view.findText("")
        self.hide()
        self.close_requested.emit()

    def _on_text_changed(self, text: str):
        if not self.active_view:
            return
        if not text:
            self.active_view.findText("")
        else:
            self.active_view.findText(text)

    def find_next(self):
        query = self.input_field.text()
        if query and self.active_view:
            self.active_view.findText(query)

    def find_prev(self):
        query = self.input_field.text()
        if query and self.active_view:
            self.active_view.findText(query, QWebEnginePage.FindFlag.FindBackward)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_bar()
        else:
            super().keyPressEvent(event)
