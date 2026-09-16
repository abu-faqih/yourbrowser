"""
YourBrowser Core - Security & Tab Password Protection
Provides cryptographic hashing and verification for password-protected tabs and profiles.
"""

import hashlib
import os

class SecurityManager:
    """Manages password protection for individual tabs and browser profiles."""
    
    def __init__(self):
        self.tab_passwords = {} # tab_id -> hashed_password
        self.profile_passwords = {} # profile_name -> hashed_password

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with project salt."""
        salt = b"yourbrowser_secure_salt_2026"
        return hashlib.sha256(salt + password.encode('utf-8')).hexdigest()

    def set_tab_password(self, tab_id: str, password: str):
        """Set or update password protection for a specific tab."""
        if not password:
            if tab_id in self.tab_passwords:
                del self.tab_passwords[tab_id]
        else:
            self.tab_passwords[tab_id] = self.hash_password(password)

    def is_tab_protected(self, tab_id: str) -> bool:
        """Check if tab has an active password set."""
        return tab_id in self.tab_passwords

    def verify_tab_password(self, tab_id: str, candidate_password: str) -> bool:
        """Verify candidate password against tab's stored hash."""
        if tab_id not in self.tab_passwords:
            return True
        return self.tab_passwords[tab_id] == self.hash_password(candidate_password)

    def set_profile_password(self, profile_name: str, password: str):
        """Protect a browser profile with password."""
        self.profile_passwords[profile_name] = self.hash_password(password)

    def verify_profile_password(self, profile_name: str, password: str) -> bool:
        if profile_name not in self.profile_passwords:
            return True
        return self.profile_passwords[profile_name] == self.hash_password(password)
