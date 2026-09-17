"""
Unit tests for ExtensionManager and Chromium WebExtensions support.
Tests manifest parsing, script extraction, enable/disable toggle,
unpacked installation, and profile script injection.
"""

import unittest
import os
import sys
import shutil
import tempfile
import json

if "QTWEBENGINE_CHROMIUM_FLAGS" not in os.environ:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineProfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.browser_data import SettingsManager
from src.core.extension_manager import ExtensionManager, BrowserExtension

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestExtensionManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sm = SettingsManager(base_dir=self.test_dir)
        self.em = ExtensionManager(base_dir=self.test_dir, settings_manager=self.sm)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_builtin_shield_booster_discovery(self):
        """Builtin shield-booster extension must be automatically discovered."""
        ext = self.em.get_extension("shield-booster")
        self.assertIsNotNone(ext)
        self.assertEqual(ext.name, "YourBrowser Shield Booster")
        self.assertEqual(ext.manifest_version, 3)
        self.assertTrue(ext.is_builtin)
        self.assertGreater(len(ext.content_scripts), 0)

    def test_extension_enable_disable_toggle(self):
        """Extensions can be toggled on/off and state persists in settings."""
        self.assertTrue(self.em.is_extension_enabled("shield-booster"))

        self.em.set_extension_enabled("shield-booster", False)
        self.assertFalse(self.em.is_extension_enabled("shield-booster"))

        # Re-instantiate to verify persistence
        em2 = ExtensionManager(base_dir=self.test_dir, settings_manager=self.sm)
        self.assertFalse(em2.is_extension_enabled("shield-booster"))

        # Turn back on
        self.em.set_extension_enabled("shield-booster", True)
        self.assertTrue(self.em.is_extension_enabled("shield-booster"))

    def test_install_unpacked_extension(self):
        """User can install an unpacked extension from a local directory."""
        mock_ext_dir = os.path.join(self.test_dir, "mock_dark_styler")
        os.makedirs(mock_ext_dir, exist_ok=True)

        manifest = {
            "manifest_version": 3,
            "name": "Custom Styler",
            "version": "1.2.0",
            "description": "Applies custom dark mode to all websites",
            "content_scripts": [
                {
                    "matches": ["<all_urls>"],
                    "js": ["style.js"],
                    "run_at": "document_start",
                    "world": "MAIN"
                }
            ]
        }
        with open(os.path.join(mock_ext_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)

        with open(os.path.join(mock_ext_dir, "style.js"), "w") as f:
            f.write("console.log('Custom Styler active');")

        installed_ext = self.em.install_unpacked_extension(mock_ext_dir)
        self.assertIsNotNone(installed_ext)
        self.assertEqual(installed_ext.name, "Custom Styler")
        self.assertEqual(installed_ext.version, "1.2.0")
        self.assertFalse(installed_ext.is_builtin)
        self.assertTrue(self.em.is_extension_enabled(installed_ext.id))

        # Check removal
        removed = self.em.remove_extension(installed_ext.id)
        self.assertTrue(removed)
        self.assertIsNone(self.em.get_extension(installed_ext.id))

    def test_apply_to_profile_scripts(self):
        """Active extension content scripts must be injected into QWebEngineProfile."""
        profile = QWebEngineProfile(app)
        self.em.set_extension_enabled("shield-booster", True)

        injected_count = self.em.apply_to_profile(profile)
        self.assertGreater(injected_count, 0)

        # Check script presence in profile
        scripts = profile.scripts().toList()
        ext_scripts = [s for s in scripts if s.name().startswith("yb_ext_shield-booster")]
        self.assertEqual(len(ext_scripts), injected_count)


if __name__ == "__main__":
    unittest.main()
