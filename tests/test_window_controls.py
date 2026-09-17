"""
Unit tests for WindowControls, DraggableHeaderWidget, and FramelessResizeMixin.
"""

import unittest
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QPoint
from src.ui.window_controls import WindowControls, DraggableHeaderWidget, FramelessResizeMixin

app = QApplication.instance() or QApplication([])

class MockFramelessWindow(QMainWindow, FramelessResizeMixin):
    def __init__(self):
        super().__init__()
        self.use_system_title_bar = False
        self.resize(800, 600)
        self.window_controls = WindowControls(self, show_max=True)


class TestWindowControls(unittest.TestCase):
    def setUp(self):
        self.window = MockFramelessWindow()

    def test_window_controls_init(self):
        controls = self.window.window_controls
        self.assertIsNotNone(controls.min_btn)
        self.assertIsNotNone(controls.max_btn)
        self.assertIsNotNone(controls.close_btn)
        self.assertEqual(controls.min_btn.text(), "—")
        self.assertEqual(controls.max_btn.text(), "□")
        self.assertEqual(controls.close_btn.text(), "✕")

    def test_maximize_icon_update(self):
        controls = self.window.window_controls
        controls.update_maximize_icon()
        self.assertEqual(controls.max_btn.text(), "□")

    def test_edge_resize_detection(self):
        # Top-left corner
        edge = self.window.get_resize_edge(QPoint(2, 2))
        self.assertEqual(edge, Qt.Edge.LeftEdge | Qt.Edge.TopEdge)

        # Bottom-right corner
        edge = self.window.get_resize_edge(QPoint(798, 598))
        self.assertEqual(edge, Qt.Edge.RightEdge | Qt.Edge.BottomEdge)

        # Interior (no resize edge)
        edge = self.window.get_resize_edge(QPoint(400, 300))
        self.assertEqual(edge, Qt.Edge(0))

    def test_draggable_header_init(self):
        header = DraggableHeaderWidget(self.window)
        self.assertEqual(header.target_window, self.window)

if __name__ == "__main__":
    unittest.main()
