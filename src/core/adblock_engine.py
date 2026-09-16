"""
YourBrowser Core - Shield & AdBlock Engine
Intercepts network requests, blocks trackers, popups, and clickjacking traps.
"""

from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineScript
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

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

ANTI_POPUP_INJECTION = """
(() => {
    'use strict';
    
    // 1. Neutralize window.open traps
    const origOpen = window.open;
    window.open = function(url, target, features) {
        console.warn('[YourBrowser Shield] Blocked popup window.open attempt:', url);
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

    // 3. Auto-bypass stream click-traps & fake overlays (e.g. "Klik Di Mana Saja untuk Memulai Film")
    function bypassStreamTraps() {
        // Target annoying LK21 overlay banner
        const overlays = document.querySelectorAll('div, section, p, span, a');
        overlays.forEach(el => {
            const text = el.textContent || '';
            if (text.includes('Klik Di Mana Saja untuk Memulai Film') || text.includes('THIS PLAYER CONTAINS ADS')) {
                const parentBox = el.closest('div[style*="position"], .player-area, .main-player') || el;
                el.style.display = 'none';
                console.log('[YourBrowser Shield] Purged stream ad trap banner');
            }
        });

        // Trigger underlying video or play button
        const playBtn = document.getElementById('customPlayButton') || 
                        document.querySelector('.vjs-big-play-button, button.play, .play-button');
        if (playBtn && playBtn.offsetParent !== null) {
            console.log('[YourBrowser Shield] Triggered genuine play button');
            playBtn.click();
        }

        const v = document.querySelector('video');
        if (v && v.paused) {
            v.muted = false;
            v.volume = 1.0;
            v.play().catch(e => {});
        }
    }

    window.addEventListener('DOMContentLoaded', () => {
        bypassStreamTraps();
        setTimeout(bypassStreamTraps, 1000);
        setTimeout(bypassStreamTraps, 2500);
    });
    setInterval(bypassStreamTraps, 3000);

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

        is_ad = any(rule in host or rule in url for rule in AD_BLOCK_RULES)
        
        if is_ad:
            info.block(True)
            self.blocked_count += 1
            for cb in self.listeners:
                try:
                    cb(self.blocked_count, url)
                except Exception:
                    pass
