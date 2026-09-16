"""
Profile Management Module
Handles isolated browser profiles, password authentication, hidden profile states,
and session tab persistence per profile.
"""

import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional

from src.core.browser_data import BaseStorage, get_default_config_dir
from src.core.security import SecurityManager


DEFAULT_AVATAR_COLORS = [
    "#FF5500",  # Brave Orange
    "#38BDF8",  # Cyber Sky
    "#A855F7",  # Electric Purple
    "#10B981",  # Emerald Green
    "#F59E0B",  # Amber Gold
    "#EC4899",  # Neon Pink
]


class ProfileManager(BaseStorage):
    """Manages browser profiles, metadata, password protection, and isolated data paths."""

    def __init__(self, base_dir: Optional[str] = None):
        super().__init__("profiles.json", base_dir)
        self._profiles_data: Dict[str, Any] = self._load({"profiles": []})
        self.profiles_dir = os.path.join(self.base_dir, "profiles")
        os.makedirs(self.profiles_dir, exist_ok=True)

    def _get_profiles_list(self) -> List[Dict[str, Any]]:
        return self._profiles_data.setdefault("profiles", [])

    def list_profiles(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Return list of profiles. If include_hidden is False, hides profiles marked as hidden."""
        profiles = self._get_profiles_list()
        if include_hidden:
            return list(profiles)
        return [p for p in profiles if not p.get("is_hidden", False)]

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a profile by unique ID."""
        for p in self._get_profiles_list():
            if p.get("id") == profile_id:
                return dict(p)
        return None

    def create_profile(
        self,
        name: str,
        password: Optional[str] = None,
        is_hidden: bool = False,
        avatar_color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create and initialize a new isolated profile."""
        clean_name = name.strip() or "Profile"
        profile_id = str(uuid.uuid4())
        profiles = self._get_profiles_list()

        # Pick color if not specified
        if not avatar_color:
            color_index = len(profiles) % len(DEFAULT_AVATAR_COLORS)
            avatar_color = DEFAULT_AVATAR_COLORS[color_index]

        has_password = bool(password and password.strip())
        password_hash = SecurityManager.hash_password(password.strip()) if has_password else ""

        profile_entry = {
            "id": profile_id,
            "name": clean_name,
            "avatar_color": avatar_color,
            "has_password": has_password,
            "password_hash": password_hash,
            "is_hidden": bool(is_hidden),
            "created_at": int(time.time()),
            "last_active": int(time.time()),
        }

        profiles.append(profile_entry)
        self._save(self._profiles_data)

        # Create isolated profile data directory
        p_dir = self.get_profile_dir(profile_id)
        os.makedirs(p_dir, exist_ok=True)

        return dict(profile_entry)

    def update_profile(
        self,
        profile_id: str,
        name: Optional[str] = None,
        password: Optional[str] = None,
        is_hidden: Optional[bool] = None,
        avatar_color: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update existing profile metadata and settings."""
        profiles = self._get_profiles_list()
        for p in profiles:
            if p.get("id") == profile_id:
                if name is not None:
                    p["name"] = name.strip() or p["name"]
                if is_hidden is not None:
                    p["is_hidden"] = bool(is_hidden)
                if avatar_color is not None:
                    p["avatar_color"] = avatar_color
                if password is not None:
                    if password == "":
                        p["has_password"] = False
                        p["password_hash"] = ""
                    else:
                        p["has_password"] = True
                        p["password_hash"] = SecurityManager.hash_password(password.strip())
                self._save(self._profiles_data)
                return dict(p)
        return None

    def delete_profile(self, profile_id: str) -> bool:
        """Remove a profile and its metadata."""
        profiles = self._get_profiles_list()
        initial_len = len(profiles)
        self._profiles_data["profiles"] = [p for p in profiles if p.get("id") != profile_id]
        if len(self._profiles_data["profiles"]) < initial_len:
            self._save(self._profiles_data)
            return True
        return False

    def verify_password(self, profile_id: str, password: str) -> bool:
        """Verify candidate password for a profile."""
        profile = self.get_profile(profile_id)
        if not profile:
            return False
        if not profile.get("has_password", False):
            return True
        expected_hash = profile.get("password_hash", "")
        return SecurityManager.hash_password(password.strip()) == expected_hash

    def update_last_active(self, profile_id: str) -> None:
        """Update last active timestamp for sorting."""
        profiles = self._get_profiles_list()
        for p in profiles:
            if p.get("id") == profile_id:
                p["last_active"] = int(time.time())
                self._save(self._profiles_data)
                break

    def get_profile_dir(self, profile_id: str) -> str:
        """Return the isolated filesystem directory for a given profile."""
        p_dir = os.path.join(self.profiles_dir, profile_id)
        os.makedirs(p_dir, exist_ok=True)
        return p_dir

    def save_session_tabs(self, profile_id: str, tabs: List[str], active_index: int = 0) -> None:
        """Save open tab URLs and active tab index for session persistence."""
        profile_dir = self.get_profile_dir(profile_id)
        session_file = os.path.join(profile_dir, "session_tabs.json")
        data = {
            "tabs": [t for t in tabs if t and not t.startswith("about:") and not t.startswith("data:")],
            "active_index": max(0, active_index),
            "saved_at": int(time.time())
        }
        temp_file = f"{session_file}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, session_file)
        except OSError as e:
            print(f"[YourBrowser Session Warning] Failed to save session tabs for {profile_id}: {e}")

    def load_session_tabs(self, profile_id: str) -> Dict[str, Any]:
        """Load persisted session tabs for a profile."""
        profile_dir = self.get_profile_dir(profile_id)
        session_file = os.path.join(profile_dir, "session_tabs.json")
        if not os.path.exists(session_file):
            return {"tabs": [], "active_index": 0}
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "tabs": data.get("tabs", []),
                    "active_index": data.get("active_index", 0)
                }
        except (json.JSONDecodeError, OSError):
            return {"tabs": [], "active_index": 0}
