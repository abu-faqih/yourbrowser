"""
Unit tests for system dark mode detection and web color-scheme integration.
"""

import unittest
from src.core.browser_data import is_system_dark_mode, SettingsManager, DEFAULT_SETTINGS


class TestDarkModeIntegration(unittest.TestCase):
    def test_is_system_dark_mode_returns_bool(self):
        res = is_system_dark_mode()
        self.assertIsInstance(res, bool)

    def test_settings_has_web_dark_mode(self):
        self.assertIn("web_dark_mode", DEFAULT_SETTINGS)
        self.assertEqual(DEFAULT_SETTINGS["web_dark_mode"], "auto")

    def test_settings_manager_web_dark_mode(self):
        sm = SettingsManager()
        self.assertIn(sm.get("web_dark_mode"), ["auto", "dark", "light"])


if __name__ == "__main__":
    unittest.main()
