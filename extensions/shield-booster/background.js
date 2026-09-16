// YourBrowser Shield Booster - Background Service Worker
chrome.tabs.onCreated.addListener((tab) => {
  // If a tab is opened with suspicious ad/popunder characteristics
  if (tab.openerTabId !== undefined) {
    const url = tab.url || tab.pendingUrl || '';
    const isBlank = !url || url === 'about:blank';
    
    // Check if opener is a known streaming / media site
    chrome.tabs.get(tab.openerTabId, (openerTab) => {
      if (chrome.runtime.lastError || !openerTab) return;
      
      const openerUrl = openerTab.url || '';
      const streamingSites = ['lk21', 'mamamas.xyz', 'layarkaca', 'rebahin', 'idlix', 'dutafilm'];
      const isFromStreaming = streamingSites.some(s => openerUrl.includes(s));

      if (isFromStreaming) {
        console.warn('[YourBrowser Shield] Auto-closed popup/newtab spawned by streaming site:', tab.id, url);
        chrome.tabs.remove(tab.id);
      }
    });
  }
});
