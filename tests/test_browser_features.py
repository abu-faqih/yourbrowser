"""
Unit and Integration Tests for Browser Features
Tests Bookmarks, History, Settings, Download Manager, Zoom, and Incognito Mode.
"""

import unittest
import sys
import os
import shutil
import tempfile
from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.browser_data import BookmarkManager, HistoryManager, SettingsManager
from src.core.download_manager import DownloadTracker, DownloadItemState, DownloadManager
from src.ui.browser_window import YourBrowserWindow

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestBrowserDataManagers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.bm = BookmarkManager(base_dir=self.test_dir)
        self.hm = HistoryManager(base_dir=self.test_dir)
        self.sm = SettingsManager(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bookmark_lifecycle(self):
        url = "https://brave.com"
        title = "Brave Software"

        self.assertFalse(self.bm.is_bookmarked(url))
        entry = self.bm.add_bookmark(title, url)
        self.assertTrue(self.bm.is_bookmarked(url))
        self.assertEqual(len(self.bm.get_all()), 1)

        # Update existing title
        self.bm.add_bookmark("Updated Brave", url)
        all_bm = self.bm.get_all()
        self.assertEqual(len(all_bm), 1)
        self.assertEqual(all_bm[0]["title"], "Updated Brave")

        # Remove by URL
        self.assertTrue(self.bm.remove_by_url(url))
        self.assertFalse(self.bm.is_bookmarked(url))
        self.assertEqual(len(self.bm.get_all()), 0)

        # Re-add and remove by ID
        entry2 = self.bm.add_bookmark("Test ID", "https://example.com")
        self.assertTrue(self.bm.remove_by_id(entry2["id"]))
        self.assertEqual(len(self.bm.get_all()), 0)

    def test_history_lifecycle(self):
        self.hm.add_entry("Home", "https://search.brave.com")
        self.hm.add_entry("Python", "https://python.org")

        recent = self.hm.get_recent()
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["title"], "Python")

        # Search
        results = self.hm.search("brave")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "https://search.brave.com")

        # Ignore internal about:
        self.assertIsNone(self.hm.add_entry("Blank", "about:blank"))
        self.assertEqual(len(self.hm.get_recent()), 2)

        # Clear
        self.hm.clear()
        self.assertEqual(len(self.hm.get_recent()), 0)

    def test_settings_manager(self):
        # Default engine is brave
        self.assertEqual(self.sm.get("search_engine"), "brave")
        search_url = self.sm.get_search_url("privacy browser")
        self.assertIn("search.brave.com/search?q=privacy+browser", search_url)

        # Switch engine to duckduckgo
        self.sm.set("search_engine", "duckduckgo")
        ddg_url = self.sm.get_search_url("python 3")
        self.assertIn("duckduckgo.com/?q=python+3", ddg_url)


class TestDownloadManager(unittest.TestCase):
    def test_download_tracker_percentage(self):
        tracker = DownloadTracker("dl-1")
        tracker.total_bytes = 1000
        tracker.received_bytes = 500
        self.assertEqual(tracker.percentage, 50)

        tracker.received_bytes = 1000
        self.assertEqual(tracker.percentage, 100)


class TestBrowserWindowFeatures(unittest.TestCase):
    def setUp(self):
        self.window = YourBrowserWindow(initial_url="about:blank")
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_bookmarks_bar_toggle(self):
        initial_state = self.window.bookmarks_bar.isVisible()
        self.window.toggle_bookmarks_bar()
        self.assertNotEqual(self.window.bookmarks_bar.isVisible(), initial_state)

    def test_zoom_controls(self):
        view = self.window.current_view()
        self.assertIsNotNone(view)

        # Default zoom factor is 1.0
        self.assertAlmostEqual(view.zoomFactor(), 1.0, places=1)

        self.window.zoom_in()
        self.assertGreater(view.zoomFactor(), 1.0)
        self.assertTrue(self.window.zoom_badge.isVisible())

        self.window.reset_zoom()
        self.assertAlmostEqual(view.zoomFactor(), 1.0, places=1)
        self.assertFalse(self.window.zoom_badge.isVisible())

    def test_reopen_closed_tab(self):
        self.window.add_new_tab("https://example.com")
        self.assertEqual(self.window.count(), 2)

        # Close tab 1
        self.window.close_tab(1)
        self.assertEqual(self.window.count(), 1)
        self.assertEqual(len(self.window.closed_tabs), 1)

        # Reopen
        self.window.reopen_closed_tab()
        self.assertEqual(self.window.count(), 2)

    def test_find_in_page_toggle(self):
        self.assertFalse(self.window.find_bar.isVisible())
        self.window.open_find_in_page()
        self.assertTrue(self.window.find_bar.isVisible())
        self.window.find_bar.close_bar()
        self.assertFalse(self.window.find_bar.isVisible())

    def test_incognito_mode_flag(self):
        incog_win = YourBrowserWindow(initial_url="about:blank", is_incognito=True)
        self.assertTrue(incog_win.is_incognito)
        self.assertIn("Private", incog_win.windowTitle())
        incog_win.close()


if __name__ == "__main__":
    unittest.main()
