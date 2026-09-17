"""
YourBrowser UI - Window Controls Component
Modern frameless window controls (Minimize, Maximize/Restore, Close),
draggable header helper, and native edge resizing mixin.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent


class WindowControls(QWidget):
    """Custom title bar window controls for frameless windows."""

    def __init__(self, parent_window: QMainWindow, show_max: bool = True, height: int = 34, parent=None):
        super().__init__(parent or parent_window)
        self.parent_window = parent_window
        self.show_max = show_max
        self.setFixedHeight(height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Minimize button
        self.min_btn = QPushButton("—", self)
        self.min_btn.setObjectName("win_min_btn")
        self.min_btn.setFixedSize(44, height)
        self.min_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.clicked.connect(self._on_minimize)
        layout.addWidget(self.min_btn)

        # Maximize / Restore button
        if self.show_max:
            self.max_btn = QPushButton("□", self)
            self.max_btn.setObjectName("win_max_btn")
            self.max_btn.setFixedSize(44, height)
            self.max_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.max_btn.setToolTip("Maximize")
            self.max_btn.clicked.connect(self._on_maximize_restore)
            layout.addWidget(self.max_btn)
        else:
            self.max_btn = None

        # Close button
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setObjectName("win_close_btn")
        self.close_btn.setFixedSize(46, height)
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self._on_close)
        layout.addWidget(self.close_btn)

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94A3B8;
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 13px;
                font-weight: 500;
                padding: 0;
            }
            QPushButton#win_min_btn:hover,
            QPushButton#win_max_btn:hover {
                background-color: rgba(255, 255, 255, 0.09);
                color: #FFFFFF;
            }
            QPushButton#win_min_btn:pressed,
            QPushButton#win_max_btn:pressed {
                background-color: rgba(255, 255, 255, 0.16);
            }
            QPushButton#win_close_btn:hover {
                background-color: #E11D48;
                color: #FFFFFF;
            }
            QPushButton#win_close_btn:pressed {
                background-color: #BE123C;
            }
        """)

    def _on_minimize(self):
        self.parent_window.showMinimized()

    def _on_maximize_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
        self.update_maximize_icon()

    def _on_close(self):
        self.parent_window.close()

    def update_maximize_icon(self):
        """Update maximize/restore icon depending on current window state."""
        if not self.max_btn:
            return
        if self.parent_window.isMaximized():
            self.max_btn.setText("❐")
            self.max_btn.setToolTip("Restore Down")
        else:
            self.max_btn.setText("□")
            self.max_btn.setToolTip("Maximize")


class DraggableHeaderWidget(QWidget):
    """Widget container that supports native system window move and double-click maximize."""

    def __init__(self, target_window: QMainWindow, parent=None):
        super().__init__(parent or target_window)
        self.target_window = target_window

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            wh = self.target_window.windowHandle()
            if wh:
                wh.startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.target_window.isMaximized():
                self.target_window.showNormal()
            else:
                self.target_window.showMaximized()
            if hasattr(self.target_window, "window_controls") and self.target_window.window_controls:
                self.target_window.window_controls.update_maximize_icon()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class FramelessResizeMixin:
    """Mixin providing edge resizing and cursor updates for frameless windows."""

    RESIZE_MARGIN = 6

    def get_resize_edge(self, pos: QPoint) -> Qt.Edge:
        if self.isMaximized() or self.isFullScreen():
            return Qt.Edge(0)
        rect = self.rect()
        w, h = rect.width(), rect.height()
        x, y = pos.x(), pos.y()
        edge = Qt.Edge(0)
        if x <= self.RESIZE_MARGIN:
            edge |= Qt.Edge.LeftEdge
        elif x >= w - self.RESIZE_MARGIN:
            edge |= Qt.Edge.RightEdge
        if y <= self.RESIZE_MARGIN:
            edge |= Qt.Edge.TopEdge
        elif y >= h - self.RESIZE_MARGIN:
            edge |= Qt.Edge.BottomEdge
        return edge

    def update_cursor_for_edge(self, edge: Qt.Edge):
        if edge in (Qt.Edge.LeftEdge | Qt.Edge.TopEdge, Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in (Qt.Edge.RightEdge | Qt.Edge.TopEdge, Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edge & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def handle_frameless_mouse_press(self, event: QMouseEvent) -> bool:
        if getattr(self, "use_system_title_bar", False) or self.isMaximized() or self.isFullScreen():
            return False
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self.get_resize_edge(event.position().toPoint())
            if edge != Qt.Edge(0):
                wh = self.windowHandle()
                if wh:
                    wh.startSystemResize(edge)
                    event.accept()
                    return True
        return False

    def handle_frameless_mouse_move(self, event: QMouseEvent) -> bool:
        if getattr(self, "use_system_title_bar", False) or self.isMaximized() or self.isFullScreen():
            return False
        edge = self.get_resize_edge(event.position().toPoint())
        self.update_cursor_for_edge(edge)
        return edge != Qt.Edge(0)
