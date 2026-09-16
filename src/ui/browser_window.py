"""
YourBrowser UI - Main Browser Window
Ultra-Modern, production-grade Chromium Browser with Brave Obsidian aesthetics,
Top Tab Strip, Capsule Omnibox, Brave Shields Engine, and Tab Password Protection.
"""

import uuid
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabBar, QLineEdit, QPushButton, QStackedWidget,
    QMessageBox, QProgressBar, QLabel, QFrame
)
from PyQt6.QtCore import QUrl, Qt, QTimer, QSize
from PyQt6.QtGui import QIcon
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
from src.resources.icons import create_svg_icon

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
    
    def __init__(self, tab_id, web_view, security_manager, parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.web_view = web_view
        self.security_manager = security_manager
        self.is_locked = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
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
        self.setWindowTitle("YourBrowser - Modern Privacy Browser")
        self.resize(1360, 850)
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
        
        self.interceptor = ShieldUrlInterceptor(self)
        self.interceptor.add_listener(self.on_ad_blocked)
        self.profile.setUrlRequestInterceptor(self.interceptor)

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

        # ==========================================================
        # 1. TOP TAB STRIP (At the very top, just like Brave/Chrome)
        # ==========================================================
        tab_strip_widget = QWidget(self)
        tab_strip_widget.setObjectName("top_tab_strip")
        tab_strip_layout = QHBoxLayout(tab_strip_widget)
        tab_strip_layout.setContentsMargins(8, 6, 8, 0)
        tab_strip_layout.setSpacing(4)

        self.tab_bar = QTabBar(tab_strip_widget)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        tab_strip_layout.addWidget(self.tab_bar)

        # Integrated "+" New Tab Button right next to the tabs
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
        # 2. NAVIGATION TOOLBAR (Directly below Tab Bar)
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
        self.back_btn.setToolTip("Click to go back")
        self.back_btn.clicked.connect(self.navigate_back)
        nav_layout.addWidget(self.back_btn)

        self.fwd_btn = QPushButton(nav_toolbar)
        self.fwd_btn.setProperty("class", "nav-btn")
        self.fwd_btn.setIcon(create_svg_icon("arrow_right", "#94A3B8", 18))
        self.fwd_btn.setIconSize(QSize(18, 18))
        self.fwd_btn.setToolTip("Click to go forward")
        self.fwd_btn.clicked.connect(self.navigate_forward)
        nav_layout.addWidget(self.fwd_btn)

        self.reload_btn = QPushButton(nav_toolbar)
        self.reload_btn.setProperty("class", "nav-btn")
        self.reload_btn.setIcon(create_svg_icon("refresh", "#94A3B8", 18))
        self.reload_btn.setIconSize(QSize(18, 18))
        self.reload_btn.setToolTip("Reload this page")
        self.reload_btn.clicked.connect(self.reload_page)
        nav_layout.addWidget(self.reload_btn)

        self.home_btn = QPushButton(nav_toolbar)
        self.home_btn.setProperty("class", "nav-btn")
        self.home_btn.setIcon(create_svg_icon("home", "#94A3B8", 18))
        self.home_btn.setIconSize(QSize(18, 18))
        self.home_btn.setToolTip("Open Home page")
        self.home_btn.clicked.connect(lambda: self.navigate_url("https://search.brave.com"))
        nav_layout.addWidget(self.home_btn)

        # Integrated Capsule Omnibox Frame
        omnibox_capsule = QFrame(nav_toolbar)
        omnibox_capsule.setObjectName("omnibox_capsule")
        capsule_layout = QHBoxLayout(omnibox_capsule)
        capsule_layout.setContentsMargins(6, 0, 8, 0)
        capsule_layout.setSpacing(6)

        self.ssl_icon_lbl = QLabel("🔒", omnibox_capsule)
        self.ssl_icon_lbl.setObjectName("ssl_icon_lbl")
        capsule_layout.addWidget(self.ssl_icon_lbl)

        self.omnibox = QLineEdit(omnibox_capsule)
        self.omnibox.setObjectName("omnibox_input")
        self.omnibox.setPlaceholderText("Search with Brave or enter web address...")
        self.omnibox.returnPressed.connect(self.on_omnibox_return)
        capsule_layout.addWidget(self.omnibox, stretch=1)

        self.bookmark_btn = QPushButton(omnibox_capsule)
        self.bookmark_btn.setObjectName("bookmark_btn")
        self.bookmark_btn.setIcon(create_svg_icon("star", "#64748B", 16))
        self.bookmark_btn.setIconSize(QSize(16, 16))
        self.bookmark_btn.setToolTip("Bookmark this tab")
        capsule_layout.addWidget(self.bookmark_btn)

        nav_layout.addWidget(omnibox_capsule, stretch=1)

        # Brave Shields Lion Button
        self.shield_btn = QPushButton("🛡️ 0 Blocked", nav_toolbar)
        self.shield_btn.setObjectName("shield_btn")
        self.shield_btn.setToolTip("Brave Shields - Privacy & Ad Protection")
        self.shield_btn.clicked.connect(self.show_shields_popup)
        nav_layout.addWidget(self.shield_btn)

        # Cyber Tab Lock Button
        self.lock_btn = QPushButton("🔒 Lock Tab", nav_toolbar)
        self.lock_btn.setObjectName("lock_btn")
        self.lock_btn.setToolTip("Protect this tab with password or PIN")
        self.lock_btn.clicked.connect(self.on_lock_current_tab)
        nav_layout.addWidget(self.lock_btn)

        # Menu Button (⋮)
        self.menu_btn = QPushButton(nav_toolbar)
        self.menu_btn.setProperty("class", "nav-btn")
        self.menu_btn.setIcon(create_svg_icon("menu", "#94A3B8", 18))
        self.menu_btn.setIconSize(QSize(18, 18))
        self.menu_btn.setToolTip("Customize and control YourBrowser")
        nav_layout.addWidget(self.menu_btn)

        main_layout.addWidget(nav_toolbar)

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
        # 3. WEB CONTENT AREA (Full-screen viewport stacked widget)
        # ==========================================================
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)

        # Compatibility alias for unit tests
        self.tabs = self

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
        view.setPage(page)

        container = TabContainer(tab_id, view, self.security_manager, self.stacked_widget)

        view.urlChanged.connect(lambda qurl: self.on_url_changed(qurl, container))
        view.titleChanged.connect(lambda title: self.on_title_changed(title, container))
        view.loadProgress.connect(self.on_load_progress)

        # Add to TabBar and StackedWidget
        index = self.tab_bar.addTab(create_svg_icon("tab_globe", "#94A3B8", 14), "New Tab")
        self.stacked_widget.addWidget(container)
        self.setCurrentIndex(index)

        if url:
            if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("about:"):
                url = "https://" + url
            view.load(QUrl(url))

        return view

    def close_tab(self, index):
        if self.tab_bar.count() > 1:
            widget = self.stacked_widget.widget(index)
            self.tab_bar.removeTab(index)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        else:
            self.add_new_tab()
            widget = self.stacked_widget.widget(0)
            self.tab_bar.removeTab(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

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
            if container.is_locked:
                self.lock_btn.setText("🔓 Unlock Tab")
                self.lock_btn.setStyleSheet("""
                    background-color: #EF4444;
                    color: #FFFFFF;
                    border: 1px solid #EF4444;
                    font-weight: 700;
                """)
                self.omnibox.setText("🔒 [Encrypted Tab Session]")
                self.ssl_icon_lbl.setText("🔒")
            else:
                self.lock_btn.setText("🔒 Lock Tab")
                self.lock_btn.setStyleSheet("")
                qurl = container.web_view.url()
                url_str = qurl.toString() if not qurl.isEmpty() else ""
                self.omnibox.setText(url_str)
                self.ssl_icon_lbl.setText("🔒" if url_str.startswith("https://") else "🌐")

    def on_url_changed(self, qurl, container):
        if container == self.current_container() and not container.is_locked:
            url_str = qurl.toString()
            self.omnibox.setText(url_str)
            self.ssl_icon_lbl.setText("🔒" if url_str.startswith("https://") else "🌐")

    def on_title_changed(self, title, container):
        index = self.stacked_widget.indexOf(container)
        if index != -1:
            lock_prefix = "🔒 " if container.is_locked else ""
            display_title = (title[:18] + "...") if len(title) > 18 else (title or "New Tab")
            icon = create_svg_icon("lock" if container.is_locked else "tab_globe", "#38BDF8" if container.is_locked else "#94A3B8", 14)
            self.tab_bar.setTabIcon(index, icon)
            self.tab_bar.setTabText(index, lock_prefix + display_title)

    def on_load_progress(self, progress):
        if progress < 100:
            self.progress_bar.show()
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.hide()

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
        self.shield_btn.setText(f"🛡️ {count} Blocked")

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
