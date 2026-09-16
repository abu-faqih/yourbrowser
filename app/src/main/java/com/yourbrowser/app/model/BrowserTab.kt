package com.yourbrowser.app.model

import android.webkit.WebView

data class BrowserTab(
    val id: String,
    var title: String = "New Tab",
    var url: String = "https://search.brave.com",
    var isLocked: Boolean = false,
    var passwordHash: String = "",
    var isCurrentSessionUnlocked: Boolean = false,
    var webView: WebView? = null
)
