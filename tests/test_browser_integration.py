import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui.browser_window import YourBrowserWindow

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

class TestBrowserIntegration(unittest.TestCase):
    def setUp(self):
        self.window = YourBrowserWindow(initial_url="about:blank")
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_initial_window_state(self):
        self.assertEqual(self.window.tabs.count(), 1)
        container = self.window.current_container()
        self.assertIsNotNone(container)
        self.assertFalse(container.is_locked)

    def test_tab_addition_and_closing(self):
        self.window.add_new_tab("about:blank")
        self.assertEqual(self.window.tabs.count(), 2)

        self.window.close_tab(1)
        self.assertEqual(self.window.tabs.count(), 1)

    def test_tab_password_locking_and_unlocking(self):
        container = self.window.current_container()
        tab_id = container.tab_id

        # Set tab password
        self.window.security_manager.set_tab_password(tab_id, "test_pass_123")
        self.assertTrue(self.window.security_manager.is_tab_protected(tab_id))

        # Lock tab
        container.lock_tab()
        self.window.on_title_changed(container.web_view.title(), container)
        self.window.on_tab_changed(0)
        self.assertTrue(container.is_locked)
        self.assertTrue(container.web_view.isHidden())
        self.assertFalse(container.overlay.isHidden())
        self.assertFalse(self.window.tab_bar.tabIcon(0).isNull())

        # Test unlock with correct password
        container.overlay.input_pwd.setText("test_pass_123")
        container.overlay.on_unlock()

        self.assertFalse(container.is_locked)
        self.assertFalse(container.web_view.isHidden())
        self.assertTrue(container.overlay.isHidden())
        self.assertNotIn("Encrypted Tab Session", self.window.omnibox.text())

    def test_shields_interceptor(self):
        self.assertTrue(self.window.interceptor.shields_enabled)
        self.assertEqual(self.window.interceptor.blocked_count, 0)

    def test_close_other_tabs(self):
        self.window.add_new_tab("about:blank")
        self.window.add_new_tab("about:blank")
        self.assertEqual(self.window.tabs.count(), 3)

        # Close all except index 1
        self.window.close_other_tabs(1)
        self.assertEqual(self.window.tabs.count(), 1)

    def test_tab_context_menu_lock_via_index(self):
        container = self.window.current_container()
        self.assertFalse(container.is_locked)

        # Set password directly
        self.window.security_manager.set_tab_password(container.tab_id, "tab_secure_pin")
        container.lock_tab()
        self.assertTrue(container.is_locked)

        # Unlock via helper
        self.window.unlock_tab_by_index(0)
        self.assertTrue(container.overlay.input_pwd.hasFocus() or container.is_locked)

if __name__ == "__main__":
    unittest.main()

