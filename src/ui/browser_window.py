"""
YourBrowser UI - Main Browser Window
Full-featured Chromium-based Browser with Brave Obsidian UI, Shields, and Tab Password Protection.
"""

import uuid
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QStackedWidget,
    QStatusBar, QMessageBox
)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineScript
)

from src.core.adblock_engine import ShieldUrlInterceptor, ANTI_POPUP_INJECTION
from src.core.security import SecurityManager
from src.ui.shields_panel import ShieldsPopup
from src.ui.lock_modal import SetPasswordDialog, LockedTabOverlay
from src.resources.style import BRAVE_THEME_QSS

class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage that blocks unwanted ad popups and handles new tabs safely."""
    
    def __init__(self, profile, browser_window, parent=None):
        super().__init__(profile, parent)
        self.browser_window = browser_window

    def createWindow(self, window_type):
        # Block popups/new windows if triggered automatically by ad networks
        if self.browser_window.interceptor.shields_enabled:
            # If site attempts to spawn a popup/popunder
            print("[YourBrowser Shield] Blocked window.open popup attempt")
            return None
        # Otherwise allow creating a new tab
        new_tab = self.browser_window.add_new_tab()
        return new_tab.page()

class TabContainer(QWidget):
    """Container holding QWebEngineView and its LockedTabOverlay."""
    
    def __init__(self, tab_id, web_view, security_manager, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.web_view = web_view
        self.security_manager = security_manager
        self.is_locked = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.web_view)

        self.overlay = LockedTabOverlay(self.tab_id, self.security_manager, self)
        self.overlay.unlocked.connect(self.on_unlocked)
        self.overlay.hide()
        self.layout.addWidget(self.overlay)

    def lock_tab(self):
        self.is_locked = True
        self.web_view.hide()
        self.overlay.show()

    def on_unlocked(self):
        self.is_locked = False
        self.overlay.hide()
        self.web_view.show()

class YourBrowserWindow(QMainWindow):
    """Main Application Window for YourBrowser."""
    
    def __init__(self, initial_url="https://search.brave.com"):
        super().__init__()
        self.setWindowTitle("YourBrowser - Privacy & Shields Browser")
        self.resize(1280, 800)
        self.setStyleSheet(BRAVE_THEME_QSS)

        self.security_manager = SecurityManager()
        self.init_web_profile()
        self.setup_ui()

        # Add initial tab
        self.add_new_tab(initial_url)

    def init_web_profile(self):
        """Configure WebEngine profile with Brave Shield settings and anti-popup injection."""
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Attach Shield URL Interceptor
        self.interceptor = ShieldUrlInterceptor(self)
        self.interceptor.add_listener(self.on_ad_blocked)
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Inject Anti-Popup Content Script globally
        script = QWebEngineScript()
        script.setName("anti_popup_script")
        script.setSourceCode(ANTI_POPUP_INJECTION)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        self.profile.scripts().insert(script)

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Navigation Toolbar
        nav_toolbar = QWidget(self)
        nav_toolbar.setObjectName("nav_toolbar")
        nav_layout = QHBoxLayout(nav_toolbar)
        nav_layout.setContentsMargins(8, 6, 8, 6)
        nav_layout.setSpacing(8)

        # Nav Buttons
        self.back_btn = QPushButton("◀", nav_toolbar)
        self.back_btn.setProperty("class", "nav-btn")
        self.back_btn.setToolTip("Back")
        self.back_btn.clicked.connect(self.navigate_back)
        nav_layout.addWidget(self.back_btn)

        self.fwd_btn = QPushButton("▶", nav_toolbar)
        self.fwd_btn.setProperty("class", "nav-btn")
        self.fwd_btn.setToolTip("Forward")
        self.fwd_btn.clicked.connect(self.navigate_forward)
        nav_layout.addWidget(self.fwd_btn)

        self.reload_btn = QPushButton("↻", nav_toolbar)
        self.reload_btn.setProperty("class", "nav-btn")
        self.reload_btn.setToolTip("Reload")
        self.reload_btn.clicked.connect(self.reload_page)
        nav_layout.addWidget(self.reload_btn)

        self.home_btn = QPushButton("🏠", nav_toolbar)
        self.home_btn.setProperty("class", "nav-btn")
        self.home_btn.setToolTip("Home")
        self.home_btn.clicked.connect(lambda: self.navigate_url("https://search.brave.com"))
        nav_layout.addWidget(self.home_btn)

        # Omnibox Address Bar
        self.omnibox = QLineEdit(nav_toolbar)
        self.omnibox.setObjectName("omnibox")
        self.omnibox.setPlaceholderText("Search or enter web address...")
        self.omnibox.returnPressed.connect(self.on_omnibox_return)
        nav_layout.addWidget(self.omnibox, stretch=1)

        # Brave Shield Button
        self.shield_btn = QPushButton("🛡️ Shields 0", nav_toolbar)
        self.shield_btn.setObjectName("shield_btn")
        self.shield_btn.setToolTip("Brave Shields Protection")
        self.shield_btn.clicked.connect(self.show_shields_popup)
        nav_layout.addWidget(self.shield_btn)

        # Tab Lock Button
        self.lock_btn = QPushButton("🔒 Lock Tab", nav_toolbar)
        self.lock_btn.setObjectName("lock_btn")
        self.lock_btn.setToolTip("Protect this tab with password")
        self.lock_btn.clicked.connect(self.on_lock_current_tab)
        nav_layout.addWidget(self.lock_btn)

        # New Tab Button (+)
        self.new_tab_btn = QPushButton("+", nav_toolbar)
        self.new_tab_btn.setProperty("class", "nav-btn")
        self.new_tab_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.new_tab_btn.setToolTip("New Tab")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        nav_layout.addWidget(self.new_tab_btn)

        main_layout.addWidget(nav_toolbar)

        # 2. Tabs Widget
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)

        # 3. Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("YourBrowser Ready - Brave Shields Active")

    def add_new_tab(self, url="https://search.brave.com"):
        """Create and append a new browser tab."""
        tab_id = str(uuid.uuid4())
        view = QWebEngineView()
        
        # Configure settings for video streaming and autoplay
        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)

        page = CustomWebEnginePage(self.profile, self, view)
        view.setPage(page)

        container = TabContainer(tab_id, view, self.security_manager, self.tabs)

        view.urlChanged.connect(lambda qurl: self.on_url_changed(qurl, container))
        view.titleChanged.connect(lambda title: self.on_title_changed(title, container))
        view.loadProgress.connect(self.on_load_progress)

        index = self.tabs.addTab(container, "New Tab")
        self.tabs.setCurrentIndex(index)

        if url:
            if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("about:"):
                url = "https://" + url
            view.load(QUrl(url))

        return view

    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            self.tabs.removeTab(index)
            widget.deleteLater()
        else:
            # If closing last tab, open new blank tab
            self.add_new_tab()
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            widget.deleteLater()

    def current_container(self) -> TabContainer:
        return self.tabs.currentWidget()

    def current_view(self) -> QWebEngineView:
        container = self.current_container()
        return container.web_view if container else None

    def on_tab_changed(self, index):
        container = self.current_container()
        if container:
            if container.is_locked:
                self.lock_btn.setText("🔓 Unlock Tab")
                self.lock_btn.setStyleSheet("background-color: #EF4444; color: #FFFFFF; border: 1px solid #EF4444;")
                self.omnibox.setText("🔒 [Locked Tab]")
            else:
                self.lock_btn.setText("🔒 Lock Tab")
                self.lock_btn.setStyleSheet("")
                qurl = container.web_view.url()
                self.omnibox.setText(qurl.toString() if not qurl.isEmpty() else "")

    def on_url_changed(self, qurl, container):
        if container == self.current_container() and not container.is_locked:
            self.omnibox.setText(qurl.toString())

    def on_title_changed(self, title, container):
        index = self.tabs.indexOf(container)
        if index != -1:
            lock_prefix = "🔒 " if container.is_locked else ""
            display_title = (title[:22] + "...") if len(title) > 22 else title
            self.tabs.setTabText(index, lock_prefix + display_title)

    def on_load_progress(self, progress):
        if progress < 100:
            self.status_bar.showMessage(f"Loading: {progress}%")
        else:
            self.status_bar.showMessage("YourBrowser Ready - Brave Shields Active", 3000)

    def on_omnibox_return(self):
        text = self.omnibox.text().strip()
        if not text:
            return
        if "." in text and " " not in text:
            url = text if text.startswith("http://") or text.startswith("https://") else f"https://{text}"
        else:
            url = f"https://search.brave.com/search?q={text}"
        self.navigate_url(url)

    def navigate_url(self, url_str):
        view = self.current_view()
        if view:
            view.load(QUrl(url_str))

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

    def on_ad_blocked(self, count, url):
        self.shield_btn.setText(f"🛡️ Shields {count}")

    def show_shields_popup(self):
        view = self.current_view()
        current_url = view.url().toString() if view else ""
        popup = ShieldsPopup(self.interceptor, current_url, self)
        btn_pos = self.shield_btn.mapToGlobal(self.shield_btn.rect().bottomLeft())
        popup.move(btn_pos.x() - 150, btn_pos.y() + 6)
        popup.exec()

    def on_lock_current_tab(self):
        container = self.current_container()
        if not container:
            return

        if container.is_locked:
            # Tab is currently locked -> prompt for password to unlock
            overlay = container.overlay
            overlay.input_pwd.setFocus()
        else:
            # Tab is unlocked -> prompt to set password and lock
            dlg = SetPasswordDialog(self.tabs.tabText(self.tabs.currentIndex()), self)
            if dlg.exec() == SetPasswordDialog.DialogCode.Accepted and dlg.password:
                self.security_manager.set_tab_password(container.tab_id, dlg.password)
                container.lock_tab()
                self.on_tab_changed(self.tabs.currentIndex())
                self.on_title_changed(container.web_view.title(), container)
                QMessageBox.information(
                    self, "Tab Protected",
                    "This tab has been password protected and locked.\nEnter your password to unlock."
                )
