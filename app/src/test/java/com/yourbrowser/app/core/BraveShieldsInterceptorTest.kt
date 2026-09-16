package com.yourbrowser.app.core

import org.junit.Assert.*
import org.junit.Test

class BraveShieldsInterceptorTest {

    @Test
    fun testShieldsFiltering() {
        val interceptor = BraveShieldsInterceptor()
        assertTrue(interceptor.shieldsEnabled)

        // Ad and tracker URLs
        assertTrue(interceptor.isAdOrTracker("https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"))
        assertTrue(interceptor.isAdOrTracker("https://securepubads.g.doubleclick.net/gampad/ads"))
        assertTrue(interceptor.isAdOrTracker("https://adsterra.com/script.js"))

        // Genuine content URLs
        assertFalse(interceptor.isAdOrTracker("https://search.brave.com/search?q=test"))
        assertFalse(interceptor.isAdOrTracker("https://wikipedia.org/wiki/Main_Page"))

        // Toggle Shields OFF
        interceptor.shieldsEnabled = false
        assertFalse(interceptor.isAdOrTracker("https://adsterra.com/script.js"))
    }
}
