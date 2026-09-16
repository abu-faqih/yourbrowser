"""
Integration tests for DashboardWindow and Profile Lifecycle.
Tests onboarding state, profile creation, Ctrl+H hidden profile toggling,
password protection modal verification, and browser session restoration.
"""

import unittest
import sys
import os
import shutil
import tempfile
if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.profile_manager import ProfileManager
from src.ui.dashboard_window import DashboardWindow, ProfilePasswordDialog, CreateProfileDialog
from src.ui.browser_window import YourBrowserWindow

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestDashboardIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.pm = ProfileManager(base_dir=self.test_dir)
        self.dashboard = DashboardWindow(profile_manager=self.pm)
        self.dashboard.show()

    def tearDown(self):
        self.dashboard.close()
        if self.dashboard.active_browser_window:
            self.dashboard.active_browser_window.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_dashboard_empty_onboarding(self):
        """When no profiles exist, dashboard should show onboarding prompt."""
        self.assertEqual(len(self.pm.list_profiles(include_hidden=True)), 0)
        # Content layout should contain onboarding frame
        self.assertGreater(self.dashboard.content_layout.count(), 0)

    def test_create_profile_and_refresh(self):
        """Creating a profile should refresh cards in the dashboard."""
        p = self.pm.create_profile("Trading Account", password=None, is_hidden=False)
        self.dashboard.refresh_profiles()
        self.assertEqual(len(self.pm.list_profiles()), 1)

    def test_hidden_profile_ctrl_h_toggle(self):
        """Ctrl+H should toggle visibility of hidden profiles."""
        p_normal = self.pm.create_profile("Normal Profile", is_hidden=False)
        p_hidden = self.pm.create_profile("Hidden Profile", is_hidden=True)

        # Initially hidden profile is not shown
        self.assertFalse(self.dashboard.show_hidden)
        visible = self.pm.list_profiles(include_hidden=self.dashboard.show_hidden)
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0]["id"], p_normal["id"])

        # Trigger Ctrl+H toggle
        self.dashboard.toggle_hidden_profiles()
        self.assertTrue(self.dashboard.show_hidden)
        self.assertTrue(self.dashboard.hidden_status_lbl.isVisible())

        # Now both profiles are visible
        visible_now = self.pm.list_profiles(include_hidden=self.dashboard.show_hidden)
        self.assertEqual(len(visible_now), 2)

        # Toggle back
        self.dashboard.toggle_hidden_profiles()
        self.assertFalse(self.dashboard.show_hidden)
        self.assertFalse(self.dashboard.hidden_status_lbl.isVisible())

    def test_password_dialog_verification(self):
        """ProfilePasswordDialog should accept correct password and reject wrong password."""
        p = self.pm.create_profile("Locked Profile", password="secure_pass_123")
        pid = p["id"]

        pwd_dialog = ProfilePasswordDialog("Locked Profile", pid, self.pm)
        pwd_dialog.show()
        pwd_dialog.pwd_input.setText("wrong_password")
        pwd_dialog.verify_and_accept()
        # Dialog shouldn't be accepted
        self.assertFalse(pwd_dialog.error_lbl.isHidden())
        self.assertIn("Incorrect password", pwd_dialog.error_lbl.text())

        # Correct password
        pwd_dialog.pwd_input.setText("secure_pass_123")
        pwd_dialog.verify_and_accept()
        self.assertEqual(pwd_dialog.result(), QDialog.DialogCode.Accepted)

    def test_browser_window_profile_isolation_and_tabs_persistence(self):
        """Browser window with profile should persist tabs and restore them."""
        p = self.pm.create_profile("Dev Profile")
        pid = p["id"]

        # Open browser window with this profile
        browser = YourBrowserWindow(
            initial_url="about:blank",
            profile_data=p,
            dashboard_window=self.dashboard,
            profile_manager=self.pm
        )
        browser.show()

        # Add tabs
        browser.add_new_tab("https://example.com/page1")
        browser.add_new_tab("https://example.com/page2")

        # Save session & go to dashboard
        browser.go_to_dashboard()

        # Check saved session tabs
        saved = self.pm.load_session_tabs(pid)
        self.assertIn("https://example.com/page1", saved["tabs"])
        self.assertIn("https://example.com/page2", saved["tabs"])

        # Reopen browser for the same profile: tabs must be restored
        browser2 = YourBrowserWindow(
            profile_data=p,
            dashboard_window=self.dashboard,
            profile_manager=self.pm
        )
        browser2.show()

        # Check that tabs were restored (at least 2 saved tabs restored)
        self.assertGreaterEqual(browser2.count(), 2)
        browser2.close()


if __name__ == "__main__":
    unittest.main()
