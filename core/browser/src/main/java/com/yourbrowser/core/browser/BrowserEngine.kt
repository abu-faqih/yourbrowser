package com.yourbrowser.core.browser

import android.content.Context
import org.mozilla.geckoview.GeckoSession
import org.mozilla.geckoview.GeckoView
import java.io.File

interface BrowserEngine {
    fun initialize(context: Context, isolatedProfileDir: File)
    fun createSession(isPrivate: Boolean = true): GeckoSession
    fun bindSessionToView(session: GeckoSession, geckoView: GeckoView)
    fun destroySession(session: GeckoSession)
    fun shutdown()
}
