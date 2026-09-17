"""
Browser Data Management Module
Handles persistence for Bookmarks, Browsing History, and Application Settings.
Storage is partitioned in the user's config directory (~/.config/yourbrowser/).
"""

import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional

def get_default_config_dir() -> str:
    """Determine a writable configuration directory with fallback and portable AppImage support."""
    env_dir = os.environ.get("YOURBROWSER_DATA_DIR")
    if env_dir:
        try:
            os.makedirs(env_dir, exist_ok=True)
            return env_dir
        except (OSError, PermissionError):
            pass

    # 1. Check for standard AppImage portable home/config
    appimage_path = os.environ.get("APPIMAGE")
    if appimage_path:
        appimage_dir = os.path.dirname(os.path.abspath(appimage_path))
        
        # Standard AppImage portable home: <AppImageName>.home
        appimage_home = f"{appimage_path}.home"
        if os.path.exists(appimage_home):
            portable_cfg = os.path.join(appimage_home, ".config", "yourbrowser")
            try:
                os.makedirs(portable_cfg, exist_ok=True)
                return portable_cfg
            except (OSError, PermissionError):
                pass

        # Standard AppImage portable config: <AppImageName>.config
        appimage_config = f"{appimage_path}.config"
        if os.path.exists(appimage_config):
            portable_cfg = os.path.join(appimage_config, "yourbrowser")
            try:
                os.makedirs(portable_cfg, exist_ok=True)
                return portable_cfg
            except (OSError, PermissionError):
                pass

        # Automatic adjacent portable directory alongside AppImage: <AppImageDir>/yourbrowser_data
        adjacent_data = os.path.join(appimage_dir, "yourbrowser_data")
        try:
            os.makedirs(adjacent_data, exist_ok=True)
            test_file = os.path.join(adjacent_data, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return adjacent_data
        except (OSError, PermissionError):
            pass

    # 2. Check for local adjacent portable directory in working directory
    local_portable = os.path.join(os.getcwd(), "yourbrowser_data")
    if os.path.exists(local_portable):
        return local_portable

    # 3. Standard system user configuration directory
    candidate = os.path.expanduser("~/.config/yourbrowser")
    try:
        os.makedirs(candidate, exist_ok=True)
        test_file = os.path.join(candidate, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return candidate
    except (OSError, PermissionError):
        # Fallback to current working directory or /tmp
        fallback = os.path.join(os.getcwd(), ".browser_data")
        try:
            os.makedirs(fallback, exist_ok=True)
            return fallback
        except (OSError, PermissionError):
            tmp_fallback = "/tmp/yourbrowser_data"
            os.makedirs(tmp_fallback, exist_ok=True)
            return tmp_fallback

def is_system_dark_mode() -> bool:
    """Detect whether Linux desktop or OS environment prefers dark mode."""
    import subprocess
    for cmd in [
        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
        ["gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"],
        ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
    ]:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip().lower()
            if "dark" in out or "prefer-dark" in out:
                return True
        except Exception:
            pass
    return False


DEFAULT_CONFIG_DIR = get_default_config_dir()

DEFAULT_SETTINGS = {
    # Search Engine
    "search_engine": "brave",
    "search_engines": {
        "brave": "https://search.brave.com/search?q={query}",
        "duckduckgo": "https://duckduckgo.com/?q={query}",
        "google": "https://www.google.com/search?q={query}",
        "bing": "https://www.bing.com/search?q={query}",
        "ecosia": "https://www.ecosia.org/search?q={query}",
        "qwant": "https://www.qwant.com/?q={query}"
    },
    # Navigation & URLs
    "homepage": "https://search.brave.com",
    "new_tab_url": "https://search.brave.com",

    # Appearance & Customization
    "theme_mode": "brave_dark",
    "accent_color": "orange",
    "show_home_button": True,
    "show_bookmarks_bar": False,
    "show_shields_lion": True,
    "use_system_title_bar": False,
    "web_dark_mode": "auto",

    # Brave Shields & Privacy
    "shields_enabled_by_default": True,
    "shields_ad_mode": "aggressive",
    "block_fingerprinting": True,
    "block_social_trackers": True,
    "force_https": True,
    "block_popups": True,
    "cookie_policy": "block_third_party",

    # Extensions
    "enabled_extensions": ["shield-booster"]
}


class BaseStorage:
    """Base persistent JSON storage handler with atomic-write protection."""

    def __init__(self, filename: str, base_dir: Optional[str] = None):
        self.base_dir = base_dir if base_dir else get_default_config_dir()
        self.filepath = os.path.join(self.base_dir, filename)
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError:
            pass

    def _load(self, default_data: Any) -> Any:
        if not os.path.exists(self.filepath):
            return default_data
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default_data

    def _save(self, data: Any) -> None:
        temp_file = f"{self.filepath}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.filepath)
        except (OSError, PermissionError) as e:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            # Don't crash application on readonly filesystem
            print(f"[YourBrowser Storage Warning] Cannot persist data to {self.filepath}: {e}")


class BookmarkManager(BaseStorage):
    """Manages browser bookmarks storage, addition, deletion, and status checks."""

    def __init__(self, base_dir: str = DEFAULT_CONFIG_DIR):
        super().__init__("bookmarks.json", base_dir)
        self._bookmarks: List[Dict[str, Any]] = self._load([])

    def get_all(self) -> List[Dict[str, Any]]:
        """Return a copy of all saved bookmarks."""
        return list(self._bookmarks)

    def is_bookmarked(self, url: str) -> bool:
        """Check whether a URL is already bookmarked."""
        normalized = url.strip().rstrip("/")
        for b in self._bookmarks:
            if b.get("url", "").strip().rstrip("/") == normalized:
                return True
        return False

    def add_bookmark(self, title: str, url: str, folder: str = "bar") -> Dict[str, Any]:
        """Add a bookmark or update title if URL exists. Returns the bookmark entry."""
        url_clean = url.strip()
        title_clean = title.strip() or url_clean

        for b in self._bookmarks:
            if b.get("url", "").strip().rstrip("/") == url_clean.rstrip("/"):
                b["title"] = title_clean
                self._save(self._bookmarks)
                return b

        entry = {
            "id": str(uuid.uuid4()),
            "title": title_clean,
            "url": url_clean,
            "folder": folder,
            "created_at": int(time.time())
        }
        self._bookmarks.append(entry)
        self._save(self._bookmarks)
        return entry

    def remove_by_url(self, url: str) -> bool:
        """Remove a bookmark matching URL. Returns True if removed."""
        normalized = url.strip().rstrip("/")
        initial_len = len(self._bookmarks)
        self._bookmarks = [b for b in self._bookmarks if b.get("url", "").strip().rstrip("/") != normalized]
        if len(self._bookmarks) < initial_len:
            self._save(self._bookmarks)
            return True
        return False

    def remove_by_id(self, bookmark_id: str) -> bool:
        """Remove a bookmark by unique ID."""
        initial_len = len(self._bookmarks)
        self._bookmarks = [b for b in self._bookmarks if b.get("id") != bookmark_id]
        if len(self._bookmarks) < initial_len:
            self._save(self._bookmarks)
            return True
        return False

    def clear(self) -> None:
        """Clear all bookmarks."""
        self._bookmarks = []
        self._save(self._bookmarks)


class HistoryManager(BaseStorage):
    """Manages browsing history recording, retrieval, and search."""

    def __init__(self, base_dir: str = DEFAULT_CONFIG_DIR, max_entries: int = 10000):
        super().__init__("history.json", base_dir)
        self.max_entries = max_entries
        self._history: List[Dict[str, Any]] = self._load([])

    def add_entry(self, title: str, url: str) -> Optional[Dict[str, Any]]:
        """Record a visited URL. Skips blank/system internal URLs."""
        clean_url = url.strip()
        if not clean_url or clean_url.startswith("about:") or clean_url.startswith("data:"):
            return None

        clean_title = title.strip() or clean_url
        entry = {
            "id": str(uuid.uuid4()),
            "title": clean_title,
            "url": clean_url,
            "timestamp": int(time.time())
        }

        # Insert at front for newest-first order
        self._history.insert(0, entry)
        if len(self._history) > self.max_entries:
            self._history = self._history[:self.max_entries]

        self._save(self._history)
        return entry

    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve most recent history items."""
        return self._history[:limit]

    def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search history by title or URL substring."""
        q = query.strip().lower()
        if not q:
            return self.get_recent(limit)
        results = [
            item for item in self._history
            if q in item.get("title", "").lower() or q in item.get("url", "").lower()
        ]
        return results[:limit]

    def remove_by_id(self, history_id: str) -> bool:
        """Remove single history entry by ID."""
        initial_len = len(self._history)
        self._history = [h for h in self._history if h.get("id") != history_id]
        if len(self._history) < initial_len:
            self._save(self._history)
            return True
        return False

    def clear(self) -> None:
        """Clear all browsing history."""
        self._history = []
        self._save(self._history)


class SettingsManager(BaseStorage):
    """Manages browser user preferences and search engine configurations."""

    def __init__(self, base_dir: str = DEFAULT_CONFIG_DIR):
        super().__init__("settings.json", base_dir)
        self._settings: Dict[str, Any] = self._load(DEFAULT_SETTINGS.copy())

        # Ensure all default keys exist
        modified = False
        for k, v in DEFAULT_SETTINGS.items():
            if k not in self._settings:
                self._settings[k] = v
                modified = True
        if modified:
            self._save(self._settings)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self._save(self._settings)

    def get_search_url(self, query: str) -> str:
        """Generate search URL for a query based on selected search engine."""
        import urllib.parse
        engine = self.get("search_engine", "brave")
        engines = self.get("search_engines", DEFAULT_SETTINGS["search_engines"])
        template = engines.get(engine, engines.get("brave", "https://search.brave.com/search?q={query}"))
        encoded_query = urllib.parse.quote_plus(query)
        return template.format(query=encoded_query)
