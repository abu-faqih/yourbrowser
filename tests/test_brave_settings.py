"""
Unit tests for Brave Settings and Customization engine.
Tests Brave Shields aggressive/standard options, fingerprinting, social trackers,
customization themes, and accent colors.
"""

import unittest
import os
import sys
import shutil
import tempfile

if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.browser_data import SettingsManager
from src.core.adblock_engine import ShieldUrlInterceptor
from src.resources.style import get_theme_stylesheet

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestBraveSettings(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sm = SettingsManager(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_brave_settings(self):
        """Verify all default Brave-like settings are properly populated."""
        self.assertEqual(self.sm.get("shields_ad_mode"), "aggressive")
        self.assertTrue(self.sm.get("block_fingerprinting"))
        self.assertTrue(self.sm.get("block_social_trackers"))
        self.assertTrue(self.sm.get("force_https"))
        self.assertTrue(self.sm.get("block_popups"))
        self.assertEqual(self.sm.get("cookie_policy"), "block_third_party")
        self.assertEqual(self.sm.get("theme_mode"), "brave_dark")
        self.assertEqual(self.sm.get("accent_color"), "orange")

    def test_interceptor_configuration(self):
        """Test ShieldUrlInterceptor responds to dynamic setting changes."""
        interceptor = ShieldUrlInterceptor()
        interceptor.configure_shields(enabled=True, ad_mode="aggressive", block_social=True, force_https=True)
        self.assertTrue(interceptor.shields_enabled)
        self.assertEqual(interceptor.ad_mode, "aggressive")
        self.assertTrue(interceptor.block_social)

        # Toggle shields off
        interceptor.configure_shields(enabled=False, ad_mode="off")
        self.assertFalse(interceptor.shields_enabled)

    def test_dynamic_theme_stylesheet_generation(self):
        """Test theme stylesheet generator handles all theme modes and accent colors."""
        # Brave Dark with Orange
        sheet1 = get_theme_stylesheet("brave_dark", "orange")
        self.assertIn("#FF5500", sheet1)

        # Cyber Dark with Cyan
        sheet2 = get_theme_stylesheet("cyber_dark", "cyan")
        self.assertIn("#06B6D4", sheet2)

        # Midnight OLED with Emerald
        sheet3 = get_theme_stylesheet("midnight", "emerald")
        self.assertIn("#10B981", sheet3)

    def test_app_icon_and_pixmap_loading(self):
        """Test application icon and pixmap loader produces valid objects."""
        from src.resources.icons import get_app_icon, get_app_pixmap
        icon = get_app_icon()
        self.assertFalse(icon.isNull())

        pixmap = get_app_pixmap(48)
        self.assertFalse(pixmap.isNull())
        self.assertEqual(pixmap.width(), 48)
        self.assertEqual(pixmap.height(), 48)


if __name__ == "__main__":
    unittest.main()
