// YourBrowser Shield Booster - Main World Anti-Popup & Anti-Clickjacking Engine
(() => {
  'use strict';

  // 1. Intercept and neutralize window.open traps
  const originalOpen = window.open;
  window.open = function(url, target, features) {
    // If URL is empty or about:blank, or javascript:
    if (!url || url === 'about:blank' || String(url).startsWith('javascript:')) {
      console.warn('[YourBrowser Shield] Blocked blank popup request');
      return { closed: false, focus: () => {}, close: () => {} };
    }

    try {
      const parsedUrl = new URL(url, window.location.href);
      // If it looks like an ad domain or redirect
      const adKeywords = ['ad', 'pop', 'bet', 'click', 'track', 'banner', 'affiliate', 'promo', 'bonus', 'direct'];
      const isSuspicious = adKeywords.some(k => parsedUrl.hostname.includes(k) || parsedUrl.pathname.includes(k));
      
      if (isSuspicious) {
        console.warn('[YourBrowser Shield] Blocked suspicious popup:', parsedUrl.href);
        return { closed: false, focus: () => {}, close: () => {} };
      }
    } catch (e) {
      console.warn('[YourBrowser Shield] Blocked invalid popup URL:', url);
      return { closed: false, focus: () => {}, close: () => {} };
    }

    // Pass legitimate same-origin user-initiated actions if needed, otherwise block in streaming pages
    console.info('[YourBrowser Shield] Neutralized external popup:', url);
    return { closed: false, focus: () => {}, close: () => {} };
  };

  // 2. Prevent click hijacking on body / document
  const originalAddEventListener = EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener = function(type, listener, options) {
    if (type === 'click' || type === 'mousedown' || type === 'pointerdown') {
      const wrappedListener = function(event) {
        // If event target is an invisible overlay or full-page banner
        const target = event.target;
        if (target && target.tagName === 'A') {
          const href = target.getAttribute('href') || '';
          if (target.getAttribute('target') === '_blank' && (href.startsWith('http') && !href.includes(window.location.hostname))) {
            const hasVideo = !!document.querySelector('video, iframe');
            if (hasVideo && !target.closest('.nav, header, footer, .player-options')) {
              console.warn('[YourBrowser Shield] Blocked deceptive link click:', href);
              event.preventDefault();
              event.stopPropagation();
              return;
            }
          }
        }
        return listener.apply(this, arguments);
      };
      return originalAddEventListener.call(this, type, wrappedListener, options);
    }
    return originalAddEventListener.call(this, type, listener, options);
  };

  // 3. Remove deceptive full-screen overlays periodically
  function purgeOverlays() {
    const overlays = document.querySelectorAll('div[style*="z-index"][style*="fixed"], div[style*="z-index"][style*="absolute"]');
    overlays.forEach(el => {
      const style = window.getComputedStyle(el);
      const zIndex = parseInt(style.zIndex, 10);
      if (zIndex > 1000 && !el.querySelector('video, iframe, .jwplayer, .vjs-tech')) {
        const rect = el.getBoundingClientRect();
        // If it covers more than 80% of viewport and has no semantic content
        if (rect.width > window.innerWidth * 0.8 && rect.height > window.innerHeight * 0.8) {
          console.warn('[YourBrowser Shield] Removed deceptive ad overlay layer');
          el.remove();
        }
      }
    });
  }

  window.addEventListener('DOMContentLoaded', purgeOverlays);
  setInterval(purgeOverlays, 1500);

  // 4. Ensure video elements can play with sound
  document.addEventListener('play', (e) => {
    if (e.target && e.target.tagName === 'VIDEO') {
      console.log('[YourBrowser Shield] Video playback started:', e.target.src || e.target.currentSrc);
      // Auto un-mute if muted by ad networks
      if (e.target.muted && e.target.volume === 0) {
        e.target.muted = false;
        e.target.volume = 1.0;
      }
    }
  }, true);
})();
