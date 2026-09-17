"""
YourBrowser UI - Main Browser Window
Ultra-Modern, production-grade Chromium Browser with Brave Obsidian aesthetics,
Top Tab Strip, Capsule Omnibox, Brave Shields Engine, Tab Password Protection,
Bookmarks Bar & Manager, Browsing History, Download Manager, Find in Page,
Zoom Controls, Incognito Mode, and Standard Keyboard Shortcuts.
"""

import os
import uuid
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabBar, QLineEdit, QPushButton, QStackedWidget,
    QMessageBox, QProgressBar, QLabel, QFrame, QMenu,
    QSizePolicy
)
from PyQt6.QtCore import QUrl, Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineScript, QWebEngineDownloadRequest
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

from src.core.adblock_engine import ShieldUrlInterceptor, ANTI_POPUP_INJECTION
from src.core.security import SecurityManager
from src.core.browser_data import BookmarkManager, HistoryManager, SettingsManager
from src.core.download_manager import DownloadManager
from src.core.profile_manager import ProfileManager
from src.core.extension_manager import ExtensionManager
from src.ui.shields_panel import ShieldsPopup
from src.ui.lock_modal import SetPasswordDialog, LockedTabOverlay
from src.ui.bookmarks_bar import BookmarksBar
from src.ui.find_in_page import FindInPageWidget
from src.ui.history_dialog import HistoryDialog
from src.ui.bookmarks_dialog import BookmarksDialog
from src.ui.downloads_dialog import DownloadsDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.extensions_dialog import ExtensionsDialog
from src.resources.style import BRAVE_THEME_QSS, get_theme_stylesheet
from src.resources.icons import create_svg_icon, create_svg_pixmap


class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage that blocks unwanted ad popups and handles new tabs safely."""

    def __init__(self, profile, browser_window, parent=None):
        super().__init__(profile, parent)
        self.browser_window = browser_window

    def createWindow(self, window_type):
        if self.browser_window.interceptor.shields_enabled:
            print("[YourBrowser Shield] Blocked window.open popup attempt")
            return None
        new_view = self.browser_window.add_new_tab()
        return new_view.page()


class TabContainer(QWidget):
    """Container holding QWebEngineView and its LockedTabOverlay."""

    tab_unlocked = pyqtSignal()

    def __init__(self, tab_id, web_view, security_manager, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.web_view = web_view
        self.security_manager = security_manager
        self.is_locked = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.web_view, stretch=1)

        self.overlay = LockedTabOverlay(self.tab_id, self.security_manager, self)
        self.overlay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.overlay.unlocked.connect(self.on_unlocked)
        self.overlay.hide()
        self.layout.addWidget(self.overlay, stretch=1)

    def lock_tab(self):
        self.is_locked = True
        self.web_view.hide()
        self.overlay.show()

    def on_unlocked(self):
        self.is_locked = False
        self.overlay.hide()
        self.web_view.show()
        self.tab_unlocked.emit()


class YourBrowserWindow(QMainWindow):
    """Main Application Window for YourBrowser."""

    def __init__(
        self,
        initial_url="https://search.brave.com",
        is_incognito=False,
        profile_data=None,
        dashboard_window=None,
        profile_manager=None
    ):
        super().__init__()
        self.is_incognito = is_incognito
        self.profile_data = profile_data or {}
        self.profile_id = self.profile_data.get("id")
        self.dashboard_window = dashboard_window
        self.profile_manager = profile_manager or ProfileManager()

        profile_name = self.profile_data.get("name")
        title_prefix = "Private Window - " if self.is_incognito else (f"[{profile_name}] " if profile_name else "")
        self.setWindowTitle(f"{title_prefix}YourBrowser - Modern Privacy Browser")
        self.resize(1360, 850)
        self.setStyleSheet(BRAVE_THEME_QSS)

        from src.resources.icons import get_app_icon
        self.setWindowIcon(get_app_icon())

        # Core Managers with Profile Isolation
        if self.profile_id and not self.is_incognito:
            profile_dir = self.profile_manager.get_profile_dir(self.profile_id)
            self.bookmark_manager = BookmarkManager(base_dir=profile_dir)
            self.history_manager = HistoryManager(base_dir=profile_dir)
            self.settings_manager = SettingsManager(base_dir=profile_dir)
            self.extension_manager = ExtensionManager(base_dir=profile_dir, settings_manager=self.settings_manager)
        else:
            self.bookmark_manager = BookmarkManager()
            self.history_manager = HistoryManager()
            self.settings_manager = SettingsManager()
            self.extension_manager = ExtensionManager(settings_manager=self.settings_manager)

        self.security_manager = SecurityManager()
        self.download_manager = DownloadManager()

        # Closed tabs stack for Ctrl+Shift+T
        self.closed_tabs = []
        # Additional child windows tracker
        self._child_windows = []

        self.init_web_profile()
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_customization()

        # Restore saved tabs or add initial tab
        self.restore_or_init_tabs(initial_url)

    def restore_or_init_tabs(self, fallback_url="https://search.brave.com"):
        """Restore persisted session tabs for this profile, or open fallback URL."""
        if self.profile_id and not self.is_incognito:
            session = self.profile_manager.load_session_tabs(self.profile_id)
            tabs = session.get("tabs", [])
            active_idx = session.get("active_index", 0)
            if tabs:
                for url in tabs:
                    self.add_new_tab(url)
                if 0 <= active_idx < self.tab_bar.count():
                    self.setCurrentIndex(active_idx)
                return

        self.add_new_tab(fallback_url)

    def init_web_profile(self):
        """Configure WebEngine profile with Brave Shield settings and anti-popup injection."""
        if self.is_incognito:
            self.profile = QWebEngineProfile(self)
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        elif self.profile_id:
            storage_name = f"yourbrowser_profile_{self.profile_id}"
            self.profile = QWebEngineProfile(storage_name, self)
            storage_path = os.path.join(self.profile_manager.get_profile_dir(self.profile_id), "web_engine")
            os.makedirs(storage_path, exist_ok=True)
            self.profile.setPersistentStoragePath(storage_path)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        else:
            self.profile = QWebEngineProfile.defaultProfile()

        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.interceptor = ShieldUrlInterceptor(self)
        self.interceptor.configure_shields(
            enabled=self.settings_manager.get("shields_enabled_by_default", True),
            ad_mode=self.settings_manager.get("shields_ad_mode", "aggressive"),
            block_social=self.settings_manager.get("block_social_trackers", True),
            force_https=self.settings_manager.get("force_https", True)
        )
        self.interceptor.ad_blocked.connect(self.on_ad_blocked)
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Connect downloads handler
        self.profile.downloadRequested.connect(self._on_download_requested)

        # Inject Shields anti-popup script
        script = QWebEngineScript()
        script.setName("anti_popup_script")
        script.setSourceCode(ANTI_POPUP_INJECTION)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        self.profile.scripts().insert(script)

        # Inject Shields anti-fingerprinting script
        if self.settings_manager.get("block_fingerprinting", True):
            from src.core.adblock_engine import ANTI_FINGERPRINT_INJECTION
            fp_script = QWebEngineScript()
            fp_script.setName("anti_fingerprint_script")
            fp_script.setSourceCode(ANTI_FINGERPRINT_INJECTION)
            fp_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            fp_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            fp_script.setRunsOnSubFrames(True)
            self.profile.scripts().insert(fp_script)

        # Apply installed extensions to profile
        self.extension_manager.apply_to_profile(self.profile)

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================================
        # 1. TOP TAB STRIP
        # ==========================================================
        tab_strip_widget = QWidget(self)
        tab_strip_widget.setObjectName("top_tab_strip")
        tab_strip_layout = QHBoxLayout(tab_strip_widget)
        tab_strip_layout.setContentsMargins(8, 6, 8, 0)
        tab_strip_layout.setSpacing(4)

        # Incognito indicator in tab strip if private
        if self.is_incognito:
            incog_badge = QFrame(tab_strip_widget)
            incog_badge.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #6366F1);"
                "border-radius: 9999px; margin-right: 6px;"
            )
            ib_layout = QHBoxLayout(incog_badge)
            ib_layout.setContentsMargins(10, 3, 10, 3)
            ib_layout.setSpacing(5)
            ib_ico = QLabel(incog_badge)
            ib_ico.setPixmap(create_svg_pixmap("incognito", "#FFFFFF", 12))
            ib_txt = QLabel("Private", incog_badge)
            ib_txt.setStyleSheet("color: #FFFFFF; font-weight: 700; font-size: 11px;")
            ib_layout.addWidget(ib_ico)
            ib_layout.addWidget(ib_txt)
            tab_strip_layout.addWidget(incog_badge)

        self.tab_bar = QTabBar(tab_strip_widget)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setIconSize(QSize(16, 16))
        self.tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_bar.customContextMenuRequested.connect(self.on_tab_context_menu)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        tab_strip_layout.addWidget(self.tab_bar)

        # New Tab Button
        self.new_tab_btn = QPushButton(tab_strip_widget)
        self.new_tab_btn.setObjectName("new_tab_btn")
        self.new_tab_btn.setIcon(create_svg_icon("plus", "#94A3B8", 16))
        self.new_tab_btn.setIconSize(QSize(16, 16))
        self.new_tab_btn.setToolTip("Open a new tab (Ctrl+T)")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        tab_strip_layout.addWidget(self.new_tab_btn)
        tab_strip_layout.addStretch()

        main_layout.addWidget(tab_strip_widget)

        # ==========================================================
        # 2. NAVIGATION TOOLBAR
        # ==========================================================
        nav_toolbar = QWidget(self)
        nav_toolbar.setObjectName("nav_toolbar")
        nav_layout = QHBoxLayout(nav_toolbar)
        nav_layout.setContentsMargins(12, 6, 12, 6)
        nav_layout.setSpacing(8)

        # Navigation Action Buttons
        self.back_btn = QPushButton(nav_toolbar)
        self.back_btn.setProperty("class", "nav-btn")
        self.back_btn.setIcon(create_svg_icon("arrow_left", "#94A3B8", 18))
        self.back_btn.setIconSize(QSize(18, 18))
        self.back_btn.setToolTip("Click to go back (Alt+Left)")
        self.back_btn.clicked.connect(self.navigate_back)
        nav_layout.addWidget(self.back_btn)

        self.fwd_btn = QPushButton(nav_toolbar)
        self.fwd_btn.setProperty("class", "nav-btn")
        self.fwd_btn.setIcon(create_svg_icon("arrow_right", "#94A3B8", 18))
        self.fwd_btn.setIconSize(QSize(18, 18))
        self.fwd_btn.setToolTip("Click to go forward (Alt+Right)")
        self.fwd_btn.clicked.connect(self.navigate_forward)
        nav_layout.addWidget(self.fwd_btn)

        self.reload_btn = QPushButton(nav_toolbar)
        self.reload_btn.setProperty("class", "nav-btn")
        self.reload_btn.setIcon(create_svg_icon("refresh", "#94A3B8", 18))
        self.reload_btn.setIconSize(QSize(18, 18))
        self.reload_btn.setToolTip("Reload this page (Ctrl+R / F5)")
        self.reload_btn.clicked.connect(self.reload_page)
        nav_layout.addWidget(self.reload_btn)

        self.home_btn = QPushButton(nav_toolbar)
        self.home_btn.setProperty("class", "nav-btn")
        self.home_btn.setIcon(create_svg_icon("home", "#94A3B8", 18))
        self.home_btn.setIconSize(QSize(18, 18))
        self.home_btn.setToolTip("Open Home page")
        self.home_btn.clicked.connect(self.navigate_home)
        nav_layout.addWidget(self.home_btn)

        # Integrated True Pill Omnibox Frame
        self.omnibox_capsule = QFrame(nav_toolbar)
        self.omnibox_capsule.setObjectName("omnibox_capsule")
        self.omnibox_capsule.setFixedHeight(38)
        capsule_layout = QHBoxLayout(self.omnibox_capsule)
        capsule_layout.setContentsMargins(10, 0, 10, 0)
        capsule_layout.setSpacing(6)

        self.ssl_icon_lbl = QLabel(self.omnibox_capsule)
        self.ssl_icon_lbl.setObjectName("ssl_icon_lbl")
        self.ssl_icon_lbl.setPixmap(create_svg_pixmap("lock", "#10B981", 14))
        self.ssl_icon_lbl.setFixedSize(16, 16)
        capsule_layout.addWidget(self.ssl_icon_lbl)

        self.omnibox = QLineEdit(self.omnibox_capsule)
        self.omnibox.setObjectName("omnibox_input")
        self.omnibox.setPlaceholderText("Search or enter web address...")
        self.omnibox.returnPressed.connect(self.on_omnibox_return)
        capsule_layout.addWidget(self.omnibox, stretch=1)

        # Zoom level badge in omnibox
        self.zoom_badge = QLabel(self.omnibox_capsule)
        self.zoom_badge.setObjectName("zoom_badge")
        self.zoom_badge.setToolTip("Click to reset zoom to 100%")
        self.zoom_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_badge.mousePressEvent = lambda e: self.reset_zoom()
        self.zoom_badge.hide()
        capsule_layout.addWidget(self.zoom_badge)

        # Bookmark Star Button in Omnibox
        self.bookmark_btn = QPushButton(self.omnibox_capsule)
        self.bookmark_btn.setObjectName("bookmark_btn")
        self.bookmark_btn.setIcon(create_svg_icon("star", "#64748B", 16))
        self.bookmark_btn.setIconSize(QSize(16, 16))
        self.bookmark_btn.setToolTip("Bookmark this tab (Ctrl+D)")
        self.bookmark_btn.clicked.connect(self.toggle_current_bookmark)
        capsule_layout.addWidget(self.bookmark_btn)

        nav_layout.addWidget(self.omnibox_capsule, stretch=1)

        # Brave Shields Lion Button
        self.shield_btn = QPushButton(" 0 Blocked", nav_toolbar)
        self.shield_btn.setObjectName("shield_btn")
        self.shield_btn.setIcon(create_svg_icon("shield", "#FFFFFF", 16))
        self.shield_btn.setIconSize(QSize(16, 16))
        self.shield_btn.setToolTip("Brave Shields - Privacy & Ad Protection")
        self.shield_btn.clicked.connect(self.show_shields_popup)
        nav_layout.addWidget(self.shield_btn)

        # Profiles Dashboard Button
        self.dashboard_btn = QPushButton(" Dashboard", nav_toolbar)
        self.dashboard_btn.setObjectName("dashboard_btn")
        self.dashboard_btn.setIcon(create_svg_icon("dashboard", "#CBD5E1", 15))
        self.dashboard_btn.setIconSize(QSize(15, 15))
        self.dashboard_btn.setToolTip("Back to Profiles Dashboard")
        self.dashboard_btn.clicked.connect(self.go_to_dashboard)
        nav_layout.addWidget(self.dashboard_btn)

        # Extensions Button
        self.extensions_btn = QPushButton(nav_toolbar)
        self.extensions_btn.setObjectName("extensions_btn")
        self.extensions_btn.setProperty("class", "nav-btn")
        self.extensions_btn.setIcon(create_svg_icon("extension", "#94A3B8", 17))
        self.extensions_btn.setIconSize(QSize(17, 17))
        self.extensions_btn.setToolTip("Extensions Manager (Ctrl+Shift+E)")
        self.extensions_btn.clicked.connect(self.show_extensions_dialog)
        nav_layout.addWidget(self.extensions_btn)

        # Tab Lock Button (hidden from toolbar, functionality preserved via context menu)
        self.lock_btn = QPushButton(" Lock Tab", nav_toolbar)
        self.lock_btn.setIcon(create_svg_icon("lock", "#FFFFFF", 14))
        self.lock_btn.setObjectName("lock_btn")
        self.lock_btn.setToolTip("Protect this tab with password or PIN")
        self.lock_btn.clicked.connect(self.on_lock_current_tab)
        self.lock_btn.hide()

        # 3-Dots Main Menu Button (⋮)
        self.menu_btn = QPushButton(nav_toolbar)
        self.menu_btn.setProperty("class", "nav-btn")
        self.menu_btn.setIcon(create_svg_icon("menu", "#94A3B8", 18))
        self.menu_btn.setIconSize(QSize(18, 18))
        self.menu_btn.setToolTip("Customize and control YourBrowser")
        self.menu_btn.clicked.connect(self.show_main_menu)
        nav_layout.addWidget(self.menu_btn)

        main_layout.addWidget(nav_toolbar)

        # ==========================================================
        # 3. BOOKMARKS BAR (Directly below navigation toolbar)
        # ==========================================================
        self.bookmarks_bar = BookmarksBar(self.bookmark_manager, self)
        self.bookmarks_bar.open_url_requested.connect(self.navigate_url)
        self.bookmarks_bar.open_new_tab_requested.connect(lambda u: self.add_new_tab(u))
        main_layout.addWidget(self.bookmarks_bar)

        show_bm_bar = self.settings_manager.get("show_bookmarks_bar", False)
        self.bookmarks_bar.setVisible(show_bm_bar)

        # Ultra-Thin Neon Loading Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF5500, stop:1 #38BDF8);
            }
        """)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # ==========================================================
        # 4. FIND IN PAGE FLOATING / INLINE BAR
        # ==========================================================
        self.find_bar = FindInPageWidget(self)
        main_layout.addWidget(self.find_bar)

        # ==========================================================
        # 5. WEB CONTENT AREA
        # ==========================================================
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.stacked_widget, stretch=1)

        # Compatibility alias for unit tests
        self.tabs = self

    def setup_shortcuts(self):
        """Register comprehensive keyboard shortcuts matching modern browsers."""
        # Tab management
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self.close_tab(self.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, self.reopen_closed_tab)

        # Window management
        QShortcut(QKeySequence("Ctrl+N"), self, self.open_new_window)
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.open_incognito_window)

        # Page navigation & reloading
        QShortcut(QKeySequence("Ctrl+R"), self, self.reload_page)
        QShortcut(QKeySequence("F5"), self, self.reload_page)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self.reload_page)
        QShortcut(QKeySequence("Ctrl+F5"), self, self.reload_page)
        QShortcut(QKeySequence("Alt+Left"), self, self.navigate_back)
        QShortcut(QKeySequence("Alt+Right"), self, self.navigate_forward)

        # Omnibox focus
        QShortcut(QKeySequence("Ctrl+L"), self, self.focus_omnibox)
        QShortcut(QKeySequence("Alt+D"), self, self.focus_omnibox)

        # Features & Dialogs
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history_dialog)
        QShortcut(QKeySequence("Ctrl+J"), self, self.show_downloads_dialog)
        QShortcut(QKeySequence("Ctrl+D"), self, self.toggle_current_bookmark)
        QShortcut(QKeySequence("Ctrl+Shift+B"), self, self.toggle_bookmarks_bar)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, self.show_bookmarks_dialog)
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, self.show_extensions_dialog)
        QShortcut(QKeySequence("Ctrl+,"), self, self.show_settings_dialog)
        QShortcut(QKeySequence("Ctrl+F"), self, self.open_find_in_page)
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_page)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)

        # Zoom controls
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom)

        # Tab switching Ctrl+1 to Ctrl+9
        for i in range(1, 9):
            idx = i - 1
            QShortcut(QKeySequence(f"Ctrl+{i}"), self, lambda tab_i=idx: self._switch_to_tab(tab_i))
        QShortcut(QKeySequence("Ctrl+9"), self, lambda: self._switch_to_tab(self.tab_bar.count() - 1))

    # Compatibility methods to maintain identical API with QTabWidget
    def count(self):
        return self.tab_bar.count()

    def currentIndex(self):
        return self.tab_bar.currentIndex()

    def currentWidget(self):
        return self.stacked_widget.currentWidget()

    def widget(self, index):
        return self.stacked_widget.widget(index)

    def tabText(self, index):
        return self.tab_bar.tabText(index)

    def setTabText(self, index, text):
        self.tab_bar.setTabText(index, text)

    def setCurrentIndex(self, index):
        self.tab_bar.setCurrentIndex(index)
        self.stacked_widget.setCurrentIndex(index)

    def _switch_to_tab(self, index: int):
        if 0 <= index < self.tab_bar.count():
            self.setCurrentIndex(index)

    def add_new_tab(self, url="https://search.brave.com"):
        """Create and append a new modern browser tab."""
        tab_id = str(uuid.uuid4())
        view = QWebEngineView()

        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)

        page = CustomWebEnginePage(self.profile, self, view)
        page.setBackgroundColor(Qt.GlobalColor.white)
        view.setPage(page)

        container = TabContainer(tab_id, view, self.security_manager, self.stacked_widget)
        container.requested_url = url
        container.tab_unlocked.connect(lambda c=container: self.on_tab_unlocked(c))

        view.urlChanged.connect(lambda qurl: self.on_url_changed(qurl, container))
        view.titleChanged.connect(lambda title: self.on_title_changed(title, container))
        view.loadProgress.connect(self.on_load_progress)
        view.loadFinished.connect(lambda ok: self.on_load_finished(ok, container))
        page.recentlyAudibleChanged.connect(lambda audible: self.on_audio_state_changed(audible, container))

        # Add to TabBar and StackedWidget
        index = self.tab_bar.addTab(create_svg_icon("tab_globe", "#94A3B8", 14), "New Tab")
        self.stacked_widget.addWidget(container)
        self.setCurrentIndex(index)

        if url:
            if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("about:"):
                url = "https://" + url
            container.requested_url = url
            view.load(QUrl(url))

        return view

    def on_tab_unlocked(self, container: TabContainer):
        """Handle unlocking of a password-protected tab to restore tab title and active UI."""
        index = self.stacked_widget.indexOf(container)
        if index != -1:
            self.on_title_changed(container.web_view.title(), container)
            if index == self.tab_bar.currentIndex():
                self.on_tab_changed(index)

    def close_tab(self, index):
        if index < 0 or index >= self.tab_bar.count():
            return

        container = self.stacked_widget.widget(index)
        if container:
            url_str = container.web_view.url().toString() or getattr(container, "requested_url", "")
            if url_str and not url_str.startswith("about:"):
                self.closed_tabs.append(url_str)

        if self.tab_bar.count() > 1:
            widget = self.stacked_widget.widget(index)
            self.tab_bar.removeTab(index)
            self.stacked_widget.removeWidget(widget)
            if hasattr(widget, "web_view") and widget.web_view:
                page = widget.web_view.page()
                if page:
                    page.deleteLater()
            widget.deleteLater()
        else:
            self.add_new_tab()
            widget = self.stacked_widget.widget(0)
            self.tab_bar.removeTab(0)
            self.stacked_widget.removeWidget(widget)
            if hasattr(widget, "web_view") and widget.web_view:
                page = widget.web_view.page()
                if page:
                    page.deleteLater()
            widget.deleteLater()
            self.setCurrentIndex(0)

    def reopen_closed_tab(self):
        if self.closed_tabs:
            url = self.closed_tabs.pop()
            self.add_new_tab(url)

    def current_container(self) -> TabContainer:
        return self.stacked_widget.currentWidget()

    def current_view(self) -> QWebEngineView:
        container = self.current_container()
        return container.web_view if container else None

    def on_tab_changed(self, index):
        if index < 0 or index >= self.stacked_widget.count():
            return
        self.stacked_widget.setCurrentIndex(index)
        container = self.current_container()
        if container:
            # Update find bar target
            self.find_bar.set_active_view(container.web_view)

            if container.is_locked:
                self.lock_btn.setText(" Unlock Tab")
                self.lock_btn.setIcon(create_svg_icon("unlock", "#FFFFFF", 14))
                self.lock_btn.setStyleSheet("""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
                    color: #FFFFFF;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: 16px;
                    font-weight: 700;
                    padding: 6px 16px;
                """)
                self.omnibox.setText("[Encrypted Tab Session]")
                self.ssl_icon_lbl.setPixmap(create_svg_pixmap("lock", "#EF4444", 14))
                self.update_bookmark_icon("")
            else:
                self.lock_btn.setText(" Lock Tab")
                self.lock_btn.setIcon(create_svg_icon("lock", "#FFFFFF", 14))
                self.lock_btn.setStyleSheet("")
                qurl = container.web_view.url()
                url_str = qurl.toString() if not qurl.isEmpty() else ""
                self.omnibox.setText(url_str)
                is_https = url_str.startswith("https://")
                self.ssl_icon_lbl.setPixmap(create_svg_pixmap("lock" if is_https else "tab_globe", "#10B981" if is_https else "#94A3B8", 14))
                self.update_bookmark_icon(url_str)
                self.update_zoom_badge(container.web_view.zoomFactor())

    def on_url_changed(self, qurl, container):
        if container == self.current_container() and not container.is_locked:
            url_str = qurl.toString()
            self.omnibox.setText(url_str)
            is_https = url_str.startswith("https://")
            self.ssl_icon_lbl.setPixmap(create_svg_pixmap("lock" if is_https else "tab_globe", "#10B981" if is_https else "#94A3B8", 14))
            self.update_bookmark_icon(url_str)

    def on_title_changed(self, title, container):
        index = self.stacked_widget.indexOf(container)
        if index != -1:
            display_title = (title[:18] + "...") if len(title) > 18 else (title or "New Tab")
            icon = create_svg_icon("lock" if container.is_locked else "tab_globe", "#38BDF8" if container.is_locked else "#94A3B8", 14)
            self.tab_bar.setTabIcon(index, icon)
            self.tab_bar.setTabText(index, display_title)

    def on_load_progress(self, progress):
        if progress < 100:
            self.progress_bar.show()
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.hide()

    def on_load_finished(self, ok: bool, container: TabContainer):
        if ok and not self.is_incognito and not container.is_locked:
            url = container.web_view.url().toString()
            title = container.web_view.title()
            self.history_manager.add_entry(title, url)

    def on_audio_state_changed(self, audible: bool, container: TabContainer):
        index = self.stacked_widget.indexOf(container)
        if index != -1:
            if audible:
                self.tab_bar.setTabIcon(index, create_svg_icon("volume_on", "#10B981", 14))
            else:
                self.on_title_changed(container.web_view.title(), container)

    def on_omnibox_return(self):
        text = self.omnibox.text().strip()
        if not text:
            return
        if "." in text and " " not in text:
            url = text if text.startswith("http://") or text.startswith("https://") else f"https://{text}"
        else:
            url = self.settings_manager.get_search_url(text)
        self.navigate_url(url)

    def navigate_url(self, url_str):
        view = self.current_view()
        if view:
            if not url_str.startswith("http://") and not url_str.startswith("https://") and not url_str.startswith("about:"):
                url_str = "https://" + url_str
            view.load(QUrl(url_str))

    def navigate_home(self):
        homepage = self.settings_manager.get("homepage", "https://search.brave.com")
        self.navigate_url(homepage)

    def navigate_back(self):
        view = self.current_view()
        if view:
            view.back()

    def navigate_forward(self):
        view = self.current_view()
        if view:
            view.forward()

    def reload_page(self):
        view = self.current_view()
        if view:
            view.reload()

    def focus_omnibox(self):
        self.omnibox.selectAll()
        self.omnibox.setFocus()

    # ==========================================================
    # Bookmarks Operations
    # ==========================================================
    def update_bookmark_icon(self, url: str):
        if not url or url.startswith("about:"):
            self.bookmark_btn.setIcon(create_svg_icon("star", "#64748B", 16))
            return
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_btn.setIcon(create_svg_icon("star", "#F59E0B", 16))
            self.bookmark_btn.setToolTip("Bookmark saved! Click to remove")
        else:
            self.bookmark_btn.setIcon(create_svg_icon("star", "#64748B", 16))
            self.bookmark_btn.setToolTip("Bookmark this tab (Ctrl+D)")

    def toggle_current_bookmark(self):
        view = self.current_view()
        if not view:
            return
        url = view.url().toString()
        if not url or url.startswith("about:"):
            return

        title = view.title() or url
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_manager.remove_by_url(url)
            self.update_bookmark_icon(url)
        else:
            self.bookmark_manager.add_bookmark(title, url)
            self.update_bookmark_icon(url)

        self.bookmarks_bar.refresh_bookmarks()

    def toggle_bookmarks_bar(self):
        is_visible = not self.bookmarks_bar.isVisible()
        self.bookmarks_bar.setVisible(is_visible)
        self.settings_manager.set("show_bookmarks_bar", is_visible)

    def show_bookmarks_dialog(self):
        dlg = BookmarksDialog(self.bookmark_manager, self)
        dlg.open_url_requested.connect(self.navigate_url)
        dlg.open_new_tab_requested.connect(lambda u: self.add_new_tab(u))
        dlg.bookmarks_changed.connect(self.bookmarks_bar.refresh_bookmarks)
        dlg.exec()

    # ==========================================================
    # History & Downloads Dialogs
    # ==========================================================
    def show_history_dialog(self):
        dlg = HistoryDialog(self.history_manager, self)
        dlg.open_url_requested.connect(self.navigate_url)
        dlg.open_new_tab_requested.connect(lambda u: self.add_new_tab(u))
        dlg.exec()

    def show_downloads_dialog(self):
        dlg = DownloadsDialog(self.download_manager, self)
        dlg.exec()

    def _on_download_requested(self, download_item: QWebEngineDownloadRequest):
        tracker = self.download_manager.handle_download_request(download_item)
        QMessageBox.information(
            self, "Download Started",
            f"Downloading file: {tracker.filename}\nSaving to: {tracker.save_path}\nPress Ctrl+J to view download progress."
        )

    # ==========================================================
    # Find in Page (Ctrl+F)
    # ==========================================================
    def open_find_in_page(self):
        view = self.current_view()
        if view:
            self.find_bar.set_active_view(view)
            self.find_bar.open_bar()

    # ==========================================================
    # Zoom Controls
    # ==========================================================
    def zoom_in(self):
        view = self.current_view()
        if view:
            new_zoom = min(view.zoomFactor() + 0.1, 3.0)
            view.setZoomFactor(new_zoom)
            self.update_zoom_badge(new_zoom)

    def zoom_out(self):
        view = self.current_view()
        if view:
            new_zoom = max(view.zoomFactor() - 0.1, 0.3)
            view.setZoomFactor(new_zoom)
            self.update_zoom_badge(new_zoom)

    def reset_zoom(self):
        view = self.current_view()
        if view:
            view.setZoomFactor(1.0)
            self.update_zoom_badge(1.0)

    def update_zoom_badge(self, factor: float):
        pct = int(round(factor * 100))
        if pct != 100:
            self.zoom_badge.setText(f"{pct}%")
            self.zoom_badge.show()
        else:
            self.zoom_badge.hide()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def print_page(self):
        view = self.current_view()
        if not view:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            view.print(printer)

    # ==========================================================
    # Window / Incognito Launchers
    # ==========================================================
    def open_new_window(self):
        win = YourBrowserWindow(initial_url="https://search.brave.com", is_incognito=False)
        self._child_windows.append(win)
        win.show()

    def open_incognito_window(self):
        win = YourBrowserWindow(initial_url="https://search.brave.com", is_incognito=True)
        self._child_windows.append(win)
        win.show()

    # ==========================================================
    # Shields Popup & Tab Lock
    # ==========================================================
    def on_ad_blocked(self, count, url):
        self.shield_btn.setText(f" {count} Blocked")

    def show_shields_popup(self):
        view = self.current_view()
        current_url = view.url().toString() if view else ""
        popup = ShieldsPopup(self.interceptor, current_url, self)
        btn_pos = self.shield_btn.mapToGlobal(self.shield_btn.rect().bottomLeft())
        popup.move(btn_pos.x() - 140, btn_pos.y() + 8)
        popup.exec()

    def on_lock_current_tab(self):
        container = self.current_container()
        if not container:
            return

        if container.is_locked:
            overlay = container.overlay
            overlay.input_pwd.setFocus()
        else:
            dlg = SetPasswordDialog(self.tab_bar.tabText(self.tab_bar.currentIndex()), self)
            if dlg.exec() == SetPasswordDialog.DialogCode.Accepted and dlg.password:
                self.security_manager.set_tab_password(container.tab_id, dlg.password)
                container.lock_tab()
                self.on_tab_changed(self.tab_bar.currentIndex())
                self.on_title_changed(container.web_view.title(), container)
                QMessageBox.information(
                    self, "Tab Protected",
                    "Tab has been locked and encrypted with your password.\nEnter your password anytime to unlock."
                )

    # ==========================================================
    # 3-Dots Main Menu
    # ==========================================================
    def show_main_menu(self):
        menu = QMenu(self)

        # Tab & Window group
        new_tab_act = menu.addAction(create_svg_icon("plus", "#CBD5E1", 15), "New Tab\tCtrl+T")
        new_tab_act.triggered.connect(lambda: self.add_new_tab())

        new_win_act = menu.addAction("New Window\tCtrl+N")
        new_win_act.triggered.connect(self.open_new_window)

        incog_act = menu.addAction(create_svg_icon("incognito", "#C084FC", 15), "New Private Window\tCtrl+Shift+N")
        incog_act.triggered.connect(self.open_incognito_window)

        menu.addSeparator()

        # History, Downloads, Bookmarks
        hist_act = menu.addAction(create_svg_icon("history", "#CBD5E1", 15), "History\tCtrl+H")
        hist_act.triggered.connect(self.show_history_dialog)

        dl_act = menu.addAction(create_svg_icon("download", "#CBD5E1", 15), "Downloads\tCtrl+J")
        dl_act.triggered.connect(self.show_downloads_dialog)

        # Bookmarks submenu
        bm_menu = menu.addMenu(create_svg_icon("star", "#F59E0B", 15), "Bookmarks")
        bm_this_act = bm_menu.addAction("Bookmark This Tab...\tCtrl+D")
        bm_this_act.triggered.connect(self.toggle_current_bookmark)

        bm_bar_toggle_act = bm_menu.addAction("Show Bookmarks Bar\tCtrl+Shift+B")
        bm_bar_toggle_act.setCheckable(True)
        bm_bar_toggle_act.setChecked(self.bookmarks_bar.isVisible())
        bm_bar_toggle_act.triggered.connect(self.toggle_bookmarks_bar)

        bm_mgr_act = bm_menu.addAction("Bookmarks Manager\tCtrl+Shift+O")
        bm_mgr_act.triggered.connect(self.show_bookmarks_dialog)

        menu.addSeparator()

        # Zoom & Fullscreen
        zoom_in_act = menu.addAction(create_svg_icon("zoom_in", "#CBD5E1", 15), "Zoom In\tCtrl++")
        zoom_in_act.triggered.connect(self.zoom_in)

        zoom_out_act = menu.addAction(create_svg_icon("zoom_out", "#CBD5E1", 15), "Zoom Out\tCtrl+-")
        zoom_out_act.triggered.connect(self.zoom_out)

        zoom_reset_act = menu.addAction("Reset Zoom (100%)\tCtrl+0")
        zoom_reset_act.triggered.connect(self.reset_zoom)

        full_act = menu.addAction("Fullscreen\tF11")
        full_act.triggered.connect(self.toggle_fullscreen)

        menu.addSeparator()

        # Page utilities
        find_act = menu.addAction(create_svg_icon("find", "#CBD5E1", 15), "Find in Page...\tCtrl+F")
        find_act.triggered.connect(self.open_find_in_page)

        print_act = menu.addAction(create_svg_icon("print", "#CBD5E1", 15), "Print...\tCtrl+P")
        print_act.triggered.connect(self.print_page)

        menu.addSeparator()

        # Extensions & Settings
        ext_act = menu.addAction(create_svg_icon("extension", "#CBD5E1", 15), "Extensions\tCtrl+Shift+E")
        ext_act.triggered.connect(self.show_extensions_dialog)

        settings_act = menu.addAction(create_svg_icon("settings", "#CBD5E1", 15), "Settings\tCtrl+,")
        settings_act.triggered.connect(self.show_settings_dialog)

        about_act = menu.addAction("About YourBrowser")
        about_act.triggered.connect(self.show_about_dialog)

        btn_pos = self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft())
        menu.exec(btn_pos)

    def show_settings_dialog(self):
        dlg = SettingsDialog(self.settings_manager, self.extension_manager, self)
        dlg.settings_updated.connect(self.apply_customization)
        dlg.exec()

    def show_extensions_dialog(self):
        dlg = ExtensionsDialog(self.extension_manager, self)
        dlg.extensions_changed.connect(lambda: self.extension_manager.apply_to_profile(self.profile))
        dlg.exec()

    def apply_customization(self):
        """Applies theme, colors, toolbar buttons, and shield preferences live."""
        theme_mode = self.settings_manager.get("theme_mode", "brave_dark")
        accent_color = self.settings_manager.get("accent_color", "orange")
        self.setStyleSheet(get_theme_stylesheet(theme_mode, accent_color))

        if hasattr(self, "home_btn"):
            self.home_btn.setVisible(self.settings_manager.get("show_home_button", True))
        if hasattr(self, "bookmarks_bar"):
            self.bookmarks_bar.setVisible(self.settings_manager.get("show_bookmarks_bar", False))
        if hasattr(self, "shield_btn"):
            self.shield_btn.setVisible(self.settings_manager.get("show_shields_lion", True))

        if hasattr(self, "interceptor"):
            self.interceptor.configure_shields(
                enabled=self.settings_manager.get("shields_enabled_by_default", True),
                ad_mode=self.settings_manager.get("shields_ad_mode", "aggressive"),
                block_social=self.settings_manager.get("block_social_trackers", True),
                force_https=self.settings_manager.get("force_https", True)
            )

        if hasattr(self, "extension_manager") and hasattr(self, "profile"):
            self.extension_manager.apply_to_profile(self.profile)

    def show_about_dialog(self):
        QMessageBox.about(
            self, "About YourBrowser",
            "<h3>YourBrowser</h3>"
            "<p>Modern Privacy Web Browser with Brave Obsidian Aesthetics.</p>"
            "<ul>"
            "<li>Chromium QtWebEngine Core</li>"
            "<li>Brave Shields & Aggressive Ad-Blocker</li>"
            "<li>Tab Password Protection</li>"
            "<li>Full Bookmarks, History & Download Managers</li>"
            "<li>Incognito Private Browsing Mode</li>"
            "</ul>"
            "<p>Version 2.0.0 (2026 Production Edition)</p>"
        )

    # ==========================================================
    # Tab Context Menu
    # ==========================================================
    def on_tab_context_menu(self, pos):
        """Display modern context menu when right-clicking on any tab."""
        index = self.tab_bar.tabAt(pos)
        if index < 0 or index >= self.stacked_widget.count():
            return

        container = self.stacked_widget.widget(index)
        if not container:
            return

        menu = QMenu(self)

        # 1. Reload Tab
        reload_action = menu.addAction(create_svg_icon("refresh", "#CBD5E1", 15), "Reload Tab")
        reload_action.triggered.connect(lambda: container.web_view.reload())

        # 2. Duplicate Tab
        dup_action = menu.addAction(create_svg_icon("plus", "#CBD5E1", 15), "Duplicate Tab")
        dup_action.triggered.connect(lambda: self.add_new_tab(container.web_view.url().toString()))

        # Mute / Unmute
        page = container.web_view.page()
        is_muted = page.isAudioMuted()
        mute_label = "Unmute Tab" if is_muted else "Mute Tab"
        mute_icon = "volume_on" if is_muted else "volume_off"
        mute_action = menu.addAction(create_svg_icon(mute_icon, "#CBD5E1", 15), mute_label)
        mute_action.triggered.connect(lambda: page.setAudioMuted(not is_muted))

        menu.addSeparator()

        # 3. Lock / Unlock Tab
        if container.is_locked:
            lock_action = menu.addAction(create_svg_icon("unlock", "#38BDF8", 16), "Unlock Tab...")
            lock_action.triggered.connect(lambda: self.unlock_tab_by_index(index))
        else:
            lock_action = menu.addAction(create_svg_icon("lock", "#38BDF8", 16), "Lock Tab with Password...")
            lock_action.triggered.connect(lambda: self.lock_tab_by_index(index))

        menu.addSeparator()

        # 4. Close Tab
        close_action = menu.addAction(create_svg_icon("close", "#EF4444", 15), "Close Tab\tCtrl+W")
        close_action.triggered.connect(lambda: self.close_tab(index))

        # 5. Close Other Tabs
        if self.tab_bar.count() > 1:
            close_others_action = menu.addAction("Close Other Tabs")
            close_others_action.triggered.connect(lambda: self.close_other_tabs(index))

        # Reopen closed tab
        if self.closed_tabs:
            reopen_act = menu.addAction("Reopen Closed Tab\tCtrl+Shift+T")
            reopen_act.triggered.connect(self.reopen_closed_tab)

        menu.exec(self.tab_bar.mapToGlobal(pos))

    def lock_tab_by_index(self, index):
        if index < 0 or index >= self.stacked_widget.count():
            return
        container = self.stacked_widget.widget(index)
        tab_title = self.tab_bar.tabText(index)
        dlg = SetPasswordDialog(tab_title, self)
        if dlg.exec() == SetPasswordDialog.DialogCode.Accepted and dlg.password:
            self.security_manager.set_tab_password(container.tab_id, dlg.password)
            container.lock_tab()
            self.on_tab_changed(self.tab_bar.currentIndex())
            self.on_title_changed(container.web_view.title(), container)
            QMessageBox.information(
                self, "Tab Protected",
                "Tab has been locked and encrypted with password.\nEnter your password to unlock."
            )

    def unlock_tab_by_index(self, index):
        self.setCurrentIndex(index)
        container = self.stacked_widget.widget(index)
        if container and container.is_locked:
            container.overlay.input_pwd.setFocus()

    def close_other_tabs(self, keep_index):
        total = self.tab_bar.count()
        for i in reversed(range(total)):
            if i != keep_index:
                self.close_tab(i)

    def save_current_session(self):
        """Save open tab URLs to profile data for session persistence."""
        if not self.profile_id or self.is_incognito:
            return
        urls = []
        for i in range(self.stacked_widget.count()):
            container = self.stacked_widget.widget(i)
            if container and getattr(container, "web_view", None):
                qurl = container.web_view.url()
                url_str = qurl.toString() if not qurl.isEmpty() else getattr(container, "requested_url", "")
                if url_str and not url_str.startswith("about:") and not url_str.startswith("data:"):
                    urls.append(url_str)
        active_idx = self.tab_bar.currentIndex()
        self.profile_manager.save_session_tabs(self.profile_id, urls, active_idx)

    def go_to_dashboard(self):
        """Save session tabs and return to the Profile Dashboard."""
        self.save_current_session()
        if self.dashboard_window:
            self.dashboard_window.return_to_dashboard()
        else:
            from src.ui.dashboard_window import DashboardWindow
            self.dashboard_window = DashboardWindow(profile_manager=self.profile_manager)
            self.dashboard_window.show()
        self.close()

    def closeEvent(self, event):
        """Ensure session tabs are saved and web pages freed before window is closed."""
        self.save_current_session()
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            if hasattr(widget, "web_view") and widget.web_view:
                page = widget.web_view.page()
                if page:
                    page.deleteLater()
            widget.deleteLater()
        super().closeEvent(event)

