"""
Unit tests for ProfileManager module.
Verifies profile creation, isolation paths, password authentication,
hidden profile filtering, and session tab persistence.
"""

import unittest
import os
import shutil
import tempfile

from src.core.profile_manager import ProfileManager


class TestProfileManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.pm = ProfileManager(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_and_list_profiles(self):
        # Initial state should be empty
        self.assertEqual(len(self.pm.list_profiles()), 0)

        # Create normal profile
        p1 = self.pm.create_profile("Personal", password=None, is_hidden=False)
        self.assertEqual(p1["name"], "Personal")
        self.assertFalse(p1["has_password"])
        self.assertFalse(p1["is_hidden"])

        # Create hidden profile with password
        p2 = self.pm.create_profile("Vault Work", password="secure_pin_123", is_hidden=True)
        self.assertEqual(p2["name"], "Vault Work")
        self.assertTrue(p2["has_password"])
        self.assertTrue(p2["is_hidden"])

        # Listing without hidden flag should return only 1
        visible_profiles = self.pm.list_profiles(include_hidden=False)
        self.assertEqual(len(visible_profiles), 1)
        self.assertEqual(visible_profiles[0]["id"], p1["id"])

        # Listing with hidden flag should return both
        all_profiles = self.pm.list_profiles(include_hidden=True)
        self.assertEqual(len(all_profiles), 2)

    def test_password_verification(self):
        p = self.pm.create_profile("Secret Profile", password="my_password_999", is_hidden=False)
        pid = p["id"]

        # Valid password
        self.assertTrue(self.pm.verify_password(pid, "my_password_999"))
        # Invalid password
        self.assertFalse(self.pm.verify_password(pid, "wrong_pass"))
        self.assertFalse(self.pm.verify_password(pid, ""))

        # Profile without password always verifies
        p_free = self.pm.create_profile("Open Profile")
        self.assertTrue(self.pm.verify_password(p_free["id"], "anything"))
        self.assertTrue(self.pm.verify_password(p_free["id"], ""))

    def test_update_and_delete_profile(self):
        p = self.pm.create_profile("Initial Name")
        pid = p["id"]

        # Update name & hide
        updated = self.pm.update_profile(pid, name="Updated Name", is_hidden=True)
        self.assertEqual(updated["name"], "Updated Name")
        self.assertTrue(updated["is_hidden"])

        # Delete profile
        self.assertTrue(self.pm.delete_profile(pid))
        self.assertIsNone(self.pm.get_profile(pid))
        self.assertEqual(len(self.pm.list_profiles(include_hidden=True)), 0)

    def test_session_tabs_persistence(self):
        p = self.pm.create_profile("Session Profile")
        pid = p["id"]

        # Default empty session
        session = self.pm.load_session_tabs(pid)
        self.assertEqual(session["tabs"], [])
        self.assertEqual(session["active_index"], 0)

        # Save session
        tabs = ["https://brave.com", "https://github.com", "about:blank"]
        self.pm.save_session_tabs(pid, tabs, active_index=1)

        # Reload session (note: about:blank should be filtered out)
        loaded = self.pm.load_session_tabs(pid)
        self.assertEqual(loaded["tabs"], ["https://brave.com", "https://github.com"])
        self.assertEqual(loaded["active_index"], 1)

    def test_profile_directory_isolation(self):
        p1 = self.pm.create_profile("Profile 1")
        p2 = self.pm.create_profile("Profile 2")

        dir1 = self.pm.get_profile_dir(p1["id"])
        dir2 = self.pm.get_profile_dir(p2["id"])

        self.assertNotEqual(dir1, dir2)
        self.assertTrue(os.path.exists(dir1))
        self.assertTrue(os.path.exists(dir2))


if __name__ == "__main__":
    unittest.main()
