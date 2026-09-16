// YourBrowser Shield Booster - Isolated World DOM Cleaner
(() => {
  'use strict';

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // Remove iframes created by ad networks
          if (node.tagName === 'IFRAME') {
            const src = node.getAttribute('src') || '';
            if (src.includes('doubleclick') || src.includes('adnxs') || src.includes('pop') || src.includes('adsterra') || src.includes('histats')) {
              console.log('[YourBrowser Shield] Purged ad iframe:', src);
              node.remove();
            }
          }
        }
      }
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
