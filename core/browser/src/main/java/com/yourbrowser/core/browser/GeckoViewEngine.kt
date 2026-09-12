package com.yourbrowser.core.browser

import android.content.Context
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

class GeckoViewEngine(
    private val mediaSniffer: MediaSniffer
) : BrowserEngine {

    private var geckoRuntime: GeckoRuntime? = null
    private val activeSessions = mutableListOf<GeckoSession>()

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
                // Evaluasi apakah request URL adalah direct video stream (.mp4, .m3u8, dll)
                mediaSniffer.inspectNetworkResponse(
                    url = request.uri,
                    mimeType = null
                )
                return GeckoResult.fromValue(AllowOrDeny.ALLOW)
            }
        }
    }
}
