package com.yourbrowser.app.core

import android.net.Uri
import android.webkit.WebResourceResponse
import java.io.ByteArrayInputStream
import java.util.concurrent.atomic.AtomicInteger

class BraveShieldsInterceptor {

    var shieldsEnabled: Boolean = true
    private val blockedCounter = AtomicInteger(0)
    private val listeners = mutableListOf<(count: Int, url: String) -> Unit>()

    companion object {
        val AD_BLOCK_DOMAINS = setOf(
            "doubleclick.net", "googlesyndication.com", "google-analytics.com",
            "adservice.google.com", "pagead2.googlesyndication.com", "adnxs.com",
            "adsterra.com", "histats.com", "popads.net", "popcash.net", "exoclick.com",
            "propellerads.com", "trafficjunky.com", "yadro.ru", "adform.net",
            "criteo.com", "taboola.com", "outbrain.com", "scorecardresearch.com",
            "seiklasnya.js", "seiklasnya.css", "donasi.assetsy.de", "histats",
            "syndication", "monetization", "tracker", "analytics", "banner",
            "creative", "clickadu", "adx", "adriver", "smartadserver"
        )

        const val ANTI_POPUP_JS = """
            (function() {
                try {
                    window.open = function(url, target, features) {
                        console.warn('[YourBrowser Android Shield] Blocked popup window.open:', url);
                        return null;
                    };
                    document.addEventListener('click', function(e) {
                        var target = e.target;
                        if (target && target.tagName === 'A') {
                            var href = target.getAttribute('href') || '';
                            if (target.getAttribute('target') === '_blank' && !href.includes(window.location.hostname)) {
                                if (!target.closest('nav, header, footer')) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                }
                            }
                        }
                    }, true);
                } catch(e) {}
            })();
        """
    }

    fun addListener(callback: (count: Int, url: String) -> Unit) {
        listeners.add(callback)
    }

    fun getBlockedCount(): Int = blockedCounter.get()

    fun resetCount() {
        blockedCounter.set(0)
    }

    fun isAdOrTracker(url: String): Boolean {
        if (!shieldsEnabled) return false
        val lowerUrl = url.lowercase()
        val host = try {
            lowerUrl.substringAfter("://").substringBefore("/").substringBefore("?")
        } catch (e: Exception) {
            ""
        }

        return AD_BLOCK_DOMAINS.any { rule ->
            host.contains(rule) || lowerUrl.contains(rule)
        }
    }

    fun intercept(url: String): WebResourceResponse? {
        if (isAdOrTracker(url)) {
            val count = blockedCounter.incrementAndGet()
            listeners.forEach { cb ->
                try { cb(count, url) } catch (e: Exception) {}
            }
            // Return empty 204 response
            return WebResourceResponse(
                "text/plain",
                "UTF-8",
                204,
                "No Content",
                mapOf("Cache-Control" to "no-store"),
                ByteArrayInputStream(ByteArray(0))
            )
        }
        return null
    }
}
