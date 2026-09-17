"""
YourBrowser Core - Extension Manager
Handles discovery, validation, content script injection, and lifecycle
for Chromium WebExtensions (Manifest V2 and Manifest V3).
"""

import os
import json
import shutil
from typing import List, Dict, Any, Optional
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineScript
from src.core.browser_data import SettingsManager, get_default_config_dir

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILTIN_EXTENSIONS_DIR = os.path.join(PROJECT_ROOT, "extensions")


class BrowserExtension:
    """Represents an installed or discovered browser extension."""

    def __init__(self, ext_id: str, path: str, manifest: Dict[str, Any], is_builtin: bool = False):
        self.id = ext_id
        self.path = path
        self.manifest = manifest
        self.is_builtin = is_builtin

        self.name = manifest.get("name", ext_id)
        self.version = manifest.get("version", "1.0.0")
        self.description = manifest.get("description", "")
        self.manifest_version = manifest.get("manifest_version", 3)
        self.permissions = manifest.get("permissions", [])
        self.host_permissions = manifest.get("host_permissions", [])
        self.content_scripts = manifest.get("content_scripts", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "manifest_version": self.manifest_version,
            "permissions": self.permissions,
            "host_permissions": self.host_permissions,
            "is_builtin": self.is_builtin,
            "path": self.path,
        }


class ExtensionManager:
    """Manages discovery, loading, and runtime script injection for browser extensions."""

    def __init__(self, base_dir: Optional[str] = None, settings_manager: Optional[SettingsManager] = None):
        self.base_dir = base_dir if base_dir else get_default_config_dir()
        self.user_extensions_dir = os.path.join(self.base_dir, "extensions")
        os.makedirs(self.user_extensions_dir, exist_ok=True)

        self.settings_manager = settings_manager or SettingsManager(base_dir=self.base_dir)
        self.extensions: Dict[str, BrowserExtension] = {}
        self.reload_extensions()

    def reload_extensions(self):
        """Scans builtin and user directories for valid unpacked WebExtensions."""
        self.extensions.clear()

        # 1. Built-in Extensions (e.g. extensions/shield-booster)
        if os.path.exists(BUILTIN_EXTENSIONS_DIR):
            for entry in os.listdir(BUILTIN_EXTENSIONS_DIR):
                ext_path = os.path.join(BUILTIN_EXTENSIONS_DIR, entry)
                if os.path.isdir(ext_path):
                    ext = self._load_extension_from_dir(entry, ext_path, is_builtin=True)
                    if ext:
                        self.extensions[ext.id] = ext

        # 2. User Installed Extensions
        if os.path.exists(self.user_extensions_dir):
            for entry in os.listdir(self.user_extensions_dir):
                ext_path = os.path.join(self.user_extensions_dir, entry)
                if os.path.isdir(ext_path):
                    ext = self._load_extension_from_dir(entry, ext_path, is_builtin=False)
                    if ext:
                        self.extensions[ext.id] = ext

    def _load_extension_from_dir(self, ext_id: str, dir_path: str, is_builtin: bool = False) -> Optional[BrowserExtension]:
        manifest_path = os.path.join(dir_path, "manifest.json")
        if not os.path.exists(manifest_path):
            return None

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            return BrowserExtension(ext_id, dir_path, manifest, is_builtin=is_builtin)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[YourBrowser Extension Warning] Failed to parse {manifest_path}: {e}")
            return None

    def get_all_extensions(self) -> List[BrowserExtension]:
        """Returns list of all discovered extensions."""
        return list(self.extensions.values())

    def get_extension(self, ext_id: str) -> Optional[BrowserExtension]:
        return self.extensions.get(ext_id)

    def is_extension_enabled(self, ext_id: str) -> bool:
        enabled_list = self.settings_manager.get("enabled_extensions", ["shield-booster"])
        return ext_id in enabled_list

    def set_extension_enabled(self, ext_id: str, enabled: bool) -> None:
        enabled_list = list(self.settings_manager.get("enabled_extensions", ["shield-booster"]))
        if enabled and ext_id not in enabled_list:
            enabled_list.append(ext_id)
        elif not enabled and ext_id in enabled_list:
            enabled_list.remove(ext_id)
        self.settings_manager.set("enabled_extensions", enabled_list)

    def install_unpacked_extension(self, source_path: str) -> BrowserExtension:
        """Copies an unpacked extension directory into user extensions and registers it."""
        source_path = os.path.abspath(source_path)
        manifest_file = os.path.join(source_path, "manifest.json")
        if not os.path.exists(manifest_file):
            raise ValueError(f"Invalid extension folder: missing manifest.json in {source_path}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        ext_name = manifest.get("name", os.path.basename(source_path))
        # Create safe directory name
        clean_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in ext_name.lower())
        dest_dir = os.path.join(self.user_extensions_dir, clean_id)

        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(source_path, dest_dir)

        extension = BrowserExtension(clean_id, dest_dir, manifest, is_builtin=False)
        self.extensions[clean_id] = extension
        # Enable newly installed extension by default
        self.set_extension_enabled(clean_id, True)
        return extension

    def remove_extension(self, ext_id: str) -> bool:
        """Removes a user extension."""
        ext = self.extensions.get(ext_id)
        if not ext or ext.is_builtin:
            return False

        if os.path.exists(ext.path):
            shutil.rmtree(ext.path, ignore_errors=True)

        self.set_extension_enabled(ext_id, False)
        if ext_id in self.extensions:
            del self.extensions[ext_id]
        return True

    def apply_to_profile(self, profile: QWebEngineProfile) -> int:
        """
        Converts content scripts of all enabled extensions into QWebEngineScript
        and inserts them into the profile script collection.
        Returns the count of injected scripts.
        """
        scripts_collection = profile.scripts()
        # Remove existing extension scripts to prevent duplicate injection
        for s in list(scripts_collection.toList()):
            if s.name().startswith("yb_ext_"):
                scripts_collection.remove(s)

        injected_count = 0
        for ext in self.get_all_extensions():
            if not self.is_extension_enabled(ext.id):
                continue

            for idx, cs in enumerate(ext.content_scripts):
                js_files = cs.get("js", [])
                run_at_str = cs.get("run_at", "document_start")
                world_str = cs.get("world", "ISOLATED")
                all_frames = cs.get("all_frames", True)

                # Read and combine JS file contents
                combined_code = []
                for js_file in js_files:
                    full_js_path = os.path.join(ext.path, js_file)
                    if os.path.exists(full_js_path):
                        try:
                            with open(full_js_path, "r", encoding="utf-8") as f:
                                combined_code.append(f.read())
                        except OSError as e:
                            print(f"[YourBrowser Extension Warning] Failed reading {full_js_path}: {e}")

                if not combined_code:
                    continue

                full_source = "\n".join(combined_code)
                script = QWebEngineScript()
                script.setName(f"yb_ext_{ext.id}_{idx}")
                script.setSourceCode(full_source)

                # Set Injection Point
                if run_at_str == "document_start":
                    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
                else:
                    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)

                # Set Execution World
                if world_str.upper() == "MAIN":
                    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
                else:
                    script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)

                script.setRunsOnSubFrames(all_frames)
                scripts_collection.insert(script)
                injected_count += 1

        return injected_count
