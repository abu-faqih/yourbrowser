"""
YourBrowser Core - Shield & AdBlock Engine
Intercepts network requests, blocks trackers, popups, and clickjacking traps.
"""

from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineScript
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

# Comprehensive list of ad, tracker, popunder, and malware domain signatures
AD_BLOCK_RULES = {
    "doubleclick.net", "googlesyndication.com", "google-analytics.com",
    "adservice.google.com", "pagead2.googlesyndication.com", "adnxs.com",
    "adsterra.com", "histats.com", "popads.net", "popcash.net", "exoclick.com",
    "propellerads.com", "trafficjunky.com", "yadro.ru", "adform.net",
    "criteo.com", "taboola.com", "outbrain.com", "scorecardresearch.com",
    "seiklasnya.js", "seiklasnya.css", "donasi.assetsy.de", "histats",
    "syndication", "monetization", "tracker", "analytics", "banner",
    "creative", "clickadu", "adx", "adriver", "smartadserver"
}

# Content script to neutralize popunders and click hijacking at document_start
ANTI_POPUP_INJECTION = """
(() => {
    'use strict';
    
    // 1. Neutralize window.open
    const origOpen = window.open;
    window.open = function(url, target, features) {
        if (!url || url === 'about:blank' || String(url).startsWith('javascript:')) {
            console.warn('[YourBrowser Shield] Blocked blank popup');
            return null;
        }
        try {
            const parsed = new URL(url, window.location.href);
            const ads = ['ad', 'pop', 'bet', 'click', 'track', 'banner', 'affiliate', 'promo'];
            if (ads.some(k => parsed.hostname.includes(k) || parsed.pathname.includes(k))) {
                console.warn('[YourBrowser Shield] Blocked ad popup URL:', parsed.href);
                return null;
            }
        } catch (e) {
            return null;
        }
        console.info('[YourBrowser Shield] Handled popup link:', url);
        return null;
    };

    // 2. Remove click hijacking on body / full-screen invisible links
    document.addEventListener('click', (e) => {
        const target = e.target;
        if (target && target.tagName === 'A') {
            const href = target.getAttribute('href') || '';
            const isExternalBlank = target.getAttribute('target') === '_blank' && 
                                   !href.includes(window.location.hostname);
            if (isExternalBlank && !target.closest('nav, header, footer')) {
                console.warn('[YourBrowser Shield] Suppressed background link click:', href);
                e.preventDefault();
                e.stopPropagation();
            }
        }
    }, true);

    // 3. Remove high z-index overlay ads
    function removeOverlays() {
        const els = document.querySelectorAll('div[style*="z-index"]');
        els.forEach(el => {
            const z = parseInt(window.getComputedStyle(el).zIndex, 10);
            if (z > 999 && !el.querySelector('video, iframe')) {
                const rect = el.getBoundingClientRect();
                if (rect.width > window.innerWidth * 0.7 && rect.height > window.innerHeight * 0.7) {
                    el.remove();
                }
            }
        });
    }
    window.addEventListener('DOMContentLoaded', removeOverlays);
    setInterval(removeOverlays, 1500);

    // 4. Auto unmute media if video starts
    document.addEventListener('play', (e) => {
        if (e.target && e.target.tagName === 'VIDEO') {
            if (e.target.muted && e.target.volume === 0) {
                e.target.muted = false;
                e.target.volume = 1.0;
            }
        }
    }, true);
})();
"""

class ShieldUrlInterceptor(QWebEngineUrlRequestInterceptor):
    """Network interceptor enforcing Brave-like aggressive Shield protection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shields_enabled = True
        self.blocked_count = 0
        self.listeners = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        host = info.requestUrl().host().lower()

        if not self.shields_enabled:
            return

        # Check if requested URL matches known ad or tracker patterns
        is_ad = any(rule in host or rule in url for rule in AD_BLOCK_RULES)
        
        if is_ad:
            info.block(True)
            self.blocked_count += 1
            for cb in self.listeners:
                try:
                    cb(self.blocked_count, url)
                except Exception:
                    pass
