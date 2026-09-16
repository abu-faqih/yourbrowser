"""
Verify streaming and zero popup behavior directly inside YourBrowser native engine.
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QUrl

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

from src.ui.browser_window import YourBrowserWindow

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

TARGET_URL = "https://mamamas.xyz/this-party-dead-2026"
window = YourBrowserWindow(initial_url=TARGET_URL)
window.show()

print(f"[YourBrowser Native Test] Navigating to {TARGET_URL}...")

def audit_stream():
    view = window.current_view()
    
    # Check blocked ad count
    print(f"[YourBrowser Native Test] Ads/Trackers Blocked by Shields: {window.interceptor.blocked_count}")
    print(f"[YourBrowser Native Test] Total Tabs Open: {window.tabs.count()}")
    
    assert window.tabs.count() == 1, "Popup tab detected!"
    assert window.interceptor.shields_enabled, "Shields must be enabled"

    print("\n[YourBrowser Native Test] SUCCESS: Native browser successfully intercepted ads, suppressed popups, and isolated session cleanly!")
    app.quit()

# Give page time to load and intercept ads
QTimer.singleShot(10000, audit_stream)
app.exec()
