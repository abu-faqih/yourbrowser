import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.security import SecurityManager

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.sm = SecurityManager()

    def test_tab_password_lifecycle(self):
        tab_id = "tab-xyz-123"
        self.assertFalse(self.sm.is_tab_protected(tab_id))
        self.assertTrue(self.sm.verify_tab_password(tab_id, "anything"))

        # Set password
        self.sm.set_tab_password(tab_id, "secret123")
        self.assertTrue(self.sm.is_tab_protected(tab_id))

        # Test verification
        self.assertTrue(self.sm.verify_tab_password(tab_id, "secret123"))
        self.assertFalse(self.sm.verify_tab_password(tab_id, "wrong_password"))
        self.assertFalse(self.sm.verify_tab_password(tab_id, ""))

        # Clear password
        self.sm.set_tab_password(tab_id, "")
        self.assertFalse(self.sm.is_tab_protected(tab_id))
        self.assertTrue(self.sm.verify_tab_password(tab_id, "any"))

    def test_profile_password(self):
        profile = "vault_personal"
        self.sm.set_profile_password(profile, "master_pin_9999")
        self.assertTrue(self.sm.verify_profile_password(profile, "master_pin_9999"))
        self.assertFalse(self.sm.verify_profile_password(profile, "wrong_pin"))

if __name__ == "__main__":
    unittest.main()
