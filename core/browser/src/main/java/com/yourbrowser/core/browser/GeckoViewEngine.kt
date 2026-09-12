package com.yourbrowser.core.browser

import android.content.Context
import android.net.Uri
import com.yourbrowser.feature.downloader.sniffer.MediaSniffer
import org.mozilla.geckoview.AllowOrDeny
import org.mozilla.geckoview.ContentBlocking
import org.mozilla.geckoview.GeckoResult
import org.mozilla.geckoview.GeckoRuntime
import org.mozilla.geckoview.GeckoRuntimeSettings
import org.mozilla.geckoview.GeckoSession
import org.mozilla.geckoview.GeckoSessionSettings
import org.mozilla.geckoview.GeckoView
import java.io.File
import java.net.URLDecoder

class GeckoViewEngine(
    private val mediaSniffer: MediaSniffer
) : BrowserEngine {

    private var geckoRuntime: GeckoRuntime? = null
    private val activeSessions = mutableListOf<GeckoSession>()

    companion object {
        const val SCHEME_MEDIA_HOOK = "yourbrowser-media://"
        const val SCHEME_PLAYER_LAUNCH = "yourbrowser-player://"

        // Script hook JavaScript untuk mendeteksi video play dan stream XHR/Fetch di dalam webpage
        val VIDEO_SNIFFER_JS = """
            (function() {
                if (window.__YB_SNIFFER_INSTALLED__) return;
                window.__YB_SNIFFER_INSTALLED__ = true;

                function reportMedia(url) {
                    if (!url || typeof url !== 'string') return;
                    if (url.startsWith('data:') || url.startsWith('javascript:')) return;
                    try {
                        var img = document.createElement('img');
                        img.src = '$SCHEME_MEDIA_HOOK' + encodeURIComponent(url);
                        img.style.display = 'none';
                        (document.body || document.documentElement).appendChild(img);
                        setTimeout(function() { img.remove(); }, 1000);
                    } catch(e) {}
                }

                function checkMediaElement(el) {
                    if (!el) return;
                    var src = el.currentSrc || el.src;
                    if (src) reportMedia(src);
                    var sources = el.querySelectorAll('source');
                    for (var i = 0; i < sources.length; i++) {
                        if (sources[i].src) reportMedia(sources[i].src);
                    }
                }

                // 1. Hook Play event pada semua elemen video/audio
                document.addEventListener('play', function(e) {
                    if (e.target && (e.target.tagName === 'VIDEO' || e.target.tagName === 'AUDIO')) {
                        checkMediaElement(e.target);
                    }
                }, true);

                // 2. Hook DOM scan untuk video yang sudah ada di halaman
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    checkMediaElement(videos[i]);
                }

                // 3. Hook XMLHttpRequest untuk streaming HLS (m3u8) dan MP4
                var origOpen = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url) {
                    if (typeof url === 'string') {
                        var clean = url.toLowerCase().split('?')[0];
                        if (clean.endsWith('.m3u8') || clean.endsWith('.mpd') || clean.endsWith('.mp4') || clean.endsWith('.webm')) {
                            reportMedia(url);
                        }
                    }
                    return origOpen.apply(this, arguments);
                };

                // 4. Hook Fetch API
                if (window.fetch) {
                    var origFetch = window.fetch;
                    window.fetch = function(resource, init) {
                        var url = typeof resource === 'string' ? resource : (resource && resource.url);
                        if (typeof url === 'string') {
                            var clean = url.toLowerCase().split('?')[0];
                            if (clean.endsWith('.m3u8') || clean.endsWith('.mpd') || clean.endsWith('.mp4') || clean.endsWith('.webm')) {
                                reportMedia(url);
                            }
                        }
                        return origFetch.apply(this, arguments);
                    };
                }
            })();
        """.trimIndent()
    }

    override fun initialize(context: Context, isolatedProfileDir: File) {
        if (geckoRuntime != null) return

        val settings = GeckoRuntimeSettings.Builder()
            .contentBlocking(
                ContentBlocking.Settings.Builder()
                    .antiTracking(ContentBlocking.AntiTracking.DEFAULT)
                    .safeBrowsing(ContentBlocking.SafeBrowsing.DEFAULT)
                    .build()
            )
            .javaScriptEnabled(true)
            .build()

        geckoRuntime = GeckoRuntime.create(context.applicationContext, settings)
    }

    override fun createSession(isPrivate: Boolean): GeckoSession {
        val runtime = geckoRuntime ?: throw IllegalStateException("GeckoRuntime belum diinisialisasi")

        val sessionSettings = GeckoSessionSettings.Builder()
            .usePrivateMode(isPrivate)
            .useTrackingProtection(true)
            .build()

        val session = GeckoSession(sessionSettings)
        setupSessionDelegates(session)
        session.open(runtime)
        activeSessions.add(session)
        return session
    }

    override fun bindSessionToView(session: GeckoSession, geckoView: GeckoView) {
        geckoView.setSession(session)
    }

    override fun destroySession(session: GeckoSession) {
        activeSessions.remove(session)
        session.close()
    }

    override fun shutdown() {
        activeSessions.forEach { it.close() }
        activeSessions.clear()
        geckoRuntime?.shutdown()
        geckoRuntime = null
    }

    private fun setupSessionDelegates(session: GeckoSession) {
        // Navigation Delegate: Mencegat navigasi URL dan pemuatan resource
        session.navigationDelegate = object : GeckoSession.NavigationDelegate {
            override fun onCanGoBack(session: GeckoSession, canGoBack: Boolean) {}
            override fun onCanGoForward(session: GeckoSession, canGoForward: Boolean) {}
            override fun onLoadRequest(session: GeckoSession, request: GeckoSession.NavigationDelegate.LoadRequest): GeckoResult<AllowOrDeny>? {
                val uri = request.uri

                // Cek apakah ini sinyal intersepsi media atau peluncuran player dari Content Script
                if (uri.startsWith(SCHEME_MEDIA_HOOK) || uri.startsWith(SCHEME_PLAYER_LAUNCH)) {
                    val encodedMediaUrl = if (uri.startsWith(SCHEME_MEDIA_HOOK)) {
                        uri.removePrefix(SCHEME_MEDIA_HOOK)
                    } else {
                        uri.removePrefix(SCHEME_PLAYER_LAUNCH)
                    }
                    try {
                        val realMediaUrl = URLDecoder.decode(encodedMediaUrl, "UTF-8")
                        mediaSniffer.inspectNetworkResponse(url = realMediaUrl, mimeType = null)
                    } catch (_: Exception) {}
                    return GeckoResult.fromValue(AllowOrDeny.DENY)
                }

                // Evaluasi apakah request URL adalah direct video stream (.mp4, .m3u8, dll)
                mediaSniffer.inspectNetworkResponse(
                    url = uri,
                    mimeType = null
                )
                return GeckoResult.fromValue(AllowOrDeny.ALLOW)
            }
        }

        // Progress Delegate: Menyuntikkan script sniffer setiap kali halaman selesai dimuat
        session.progressDelegate = object : GeckoSession.ProgressDelegate {
            override fun onPageStop(session: GeckoSession, success: Boolean) {
                if (success) {
                    injectSnifferScript(session)
                }
            }
        }
    }

    fun injectSnifferScript(session: GeckoSession) {
        try {
            val encodedJs = Uri.encode(VIDEO_SNIFFER_JS)
            session.loadUri("javascript:(function(){try{eval(decodeURIComponent('$encodedJs'));}catch(e){}})();")
        } catch (_: Exception) {}
    }
}
