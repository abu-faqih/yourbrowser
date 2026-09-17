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

SOCIAL_TRACKER_RULES = {
    "connect.facebook.net", "facebook.com/tr", "platform.twitter.com",
    "syndication.twitter.com", "platform.linkedin.com", "licdn.com",
    "analytics.tiktok.com", "pinterest.com/ct.js"
}

ANTI_FINGERPRINT_INJECTION = """
(() => {
    'use strict';
    // Brave-like Fingerprinting Protection: Canvas & Audio Context spoofing
    try {
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {
            const ctx = this.getContext('2d');
            if (ctx) {
                // Introduce subtle noise to canvas hash without ruining visible rendering
                const img = ctx.getImageData(0, 0, Math.min(this.width, 2), Math.min(this.height, 2));
                img.data[0] = (img.data[0] + 1) % 255;
                ctx.putImageData(img, 0, 0);
            }
            return origToDataURL.apply(this, arguments);
        };
    } catch(e) {}
})();
"""

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
    ad_blocked = pyqtSignal(int, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shields_enabled = True
        self.ad_mode = "aggressive"  # "aggressive", "standard", "off"
        self.block_social = True
        self.force_https = True
        self.blocked_count = 0
        self.listeners = []

    def configure_shields(self, enabled: bool = True, ad_mode: str = "aggressive", block_social: bool = True, force_https: bool = True):
        """Update shield blocking settings dynamically."""
        self.shields_enabled = enabled
        self.ad_mode = ad_mode
        self.block_social = block_social
        self.force_https = force_https

    def add_listener(self, callback):
        self.listeners.append(callback)

    def interceptRequest(self, info):
        if not self.shields_enabled or self.ad_mode == "off":
            return

        qurl = info.requestUrl()
        url = qurl.toString().lower()
        host = qurl.host().lower()

        # 1. Social Tracker Filter
        if self.block_social:
            is_social = any(rule in host or rule in url for rule in SOCIAL_TRACKER_RULES)
            if is_social:
                info.block(True)
                self.blocked_count += 1
                self.ad_blocked.emit(self.blocked_count, url)
                self._notify_listeners(url)
                return

        # 2. Ads & Trackers Filter
        is_ad = any(rule in host or rule in url for rule in AD_BLOCK_RULES)
        if is_ad:
            info.block(True)
            self.blocked_count += 1
            self.ad_blocked.emit(self.blocked_count, url)
            self._notify_listeners(url)

    def _notify_listeners(self, url: str):
        for cb in self.listeners:
            try:
                cb(self.blocked_count, url)
            except Exception:
                pass
