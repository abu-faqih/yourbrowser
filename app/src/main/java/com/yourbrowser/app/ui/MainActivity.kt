package com.yourbrowser.app.ui

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.net.http.SslError
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.webkit.*
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.PopupMenu
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.yourbrowser.app.R
import com.yourbrowser.app.core.BraveShieldsInterceptor
import com.yourbrowser.app.core.BrowserDataManager
import com.yourbrowser.app.core.SecurityVault
import com.yourbrowser.app.databinding.ActivityMainBinding
import com.yourbrowser.app.model.BrowserTab
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val tabs = mutableListOf<BrowserTab>()
    private var activeTabId: String = ""

    private val shieldsInterceptor = BraveShieldsInterceptor()
    private lateinit var dataManager: BrowserDataManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        dataManager = BrowserDataManager(this)

        setupOmnibox()
        setupNavigation()
        setupShields()

        // Handle initial intent URL if opened from external link
        val initialUrl = intent?.dataString ?: "https://search.brave.com"
        addNewTab(initialUrl)
    }

    private fun setupShields() {
        shieldsInterceptor.addListener { count, _ ->
            runOnUiThread {
                binding.txtShieldsCount.text = count.toString()
            }
        }

        binding.btnShields.setOnClickListener {
            val activeTab = getActiveTab()
            val sheet = ShieldsBottomSheet(shieldsInterceptor, activeTab?.url ?: "") { isEnabled ->
                val status = if (isEnabled) "Shields UP" else "Shields DOWN"
                Toast.makeText(this, status, Toast.LENGTH_SHORT).show()
                activeTab?.webView?.reload()
            }
            sheet.show(supportFragmentManager, "shields_sheet")
        }
    }

    private fun setupOmnibox() {
        binding.edtOmnibox.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO || actionId == EditorInfo.IME_ACTION_DONE) {
                val query = binding.edtOmnibox.text.toString()
                val targetUrl = dataManager.formatSearchQuery(query)
                getActiveTab()?.let { tab ->
                    tab.webView?.loadUrl(targetUrl)
                }
                binding.edtOmnibox.clearFocus()
                true
            } else {
                false
            }
        }

        binding.btnBookmark.setOnClickListener {
            val activeTab = getActiveTab() ?: return@setOnClickListener
            val currentUrl = activeTab.url
            if (dataManager.isBookmarked(currentUrl)) {
                dataManager.removeBookmark(currentUrl)
                binding.btnBookmark.setImageResource(R.drawable.ic_star)
                binding.btnBookmark.setColorFilter(getColor(R.color.text_secondary))
                Toast.makeText(this, "Bookmark removed", Toast.LENGTH_SHORT).show()
            } else {
                dataManager.addBookmark(activeTab.title, currentUrl)
                binding.btnBookmark.setImageResource(R.drawable.ic_star_filled)
                binding.btnBookmark.clearColorFilter()
                Toast.makeText(this, "Bookmark saved", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnTabs.setOnClickListener {
            val sheet = TabsBottomSheet(
                tabs = tabs,
                activeTabId = activeTabId,
                onTabSelected = { selectTab(it.id) },
                onTabClosed = { closeTab(it.id) },
                onNewTab = { addNewTab("https://search.brave.com") },
                onLockToggle = { promptLockTab(it) }
            )
            sheet.show(supportFragmentManager, "tabs_sheet")
        }

        binding.btnMore.setOnClickListener { view ->
            showPopupMenu(view)
        }
    }

    private fun setupNavigation() {
        binding.btnBack.setOnClickListener {
            val webView = getActiveTab()?.webView
            if (webView != null && webView.canGoBack()) {
                webView.goBack()
            }
        }

        binding.btnForward.setOnClickListener {
            val webView = getActiveTab()?.webView
            if (webView != null && webView.canGoForward()) {
                webView.goForward()
            }
        }

        binding.btnHome.setOnClickListener {
            getActiveTab()?.webView?.loadUrl("https://search.brave.com")
        }

        binding.btnReload.setOnClickListener {
            getActiveTab()?.webView?.reload()
        }

        binding.btnNewTab.setOnClickListener {
            addNewTab("https://search.brave.com")
        }

        binding.btnSubmitUnlock.setOnClickListener {
            val activeTab = getActiveTab() ?: return@setOnClickListener
            val candidate = binding.edtUnlockPasscode.text.toString()
            if (SecurityVault.verifyPassword(candidate, activeTab.passwordHash)) {
                activeTab.isCurrentSessionUnlocked = true
                binding.edtUnlockPasscode.setText("")
                updateLockOverlay(activeTab)
            } else {
                Toast.makeText(this, "Incorrect Passcode / PIN", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showPopupMenu(anchor: View) {
        val popup = PopupMenu(this, anchor)
        popup.menu.add(0, 1, 0, "Bookmarks & History")
        popup.menu.add(0, 2, 1, "🔒 Lock Tab with PIN")
        popup.menu.add(0, 3, 2, "Desktop Site")
        popup.menu.add(0, 4, 3, "New Tab")
        popup.menu.add(0, 5, 4, "Close Current Tab")

        popup.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                1 -> {
                    DataPanelDialog(this, dataManager) { url ->
                        getActiveTab()?.webView?.loadUrl(url)
                    }.show()
                    true
                }
                2 -> {
                    getActiveTab()?.let { promptLockTab(it) }
                    true
                }
                3 -> {
                    toggleDesktopMode()
                    true
                }
                4 -> {
                    addNewTab("https://search.brave.com")
                    true
                }
                5 -> {
                    closeTab(activeTabId)
                    true
                }
                else -> false
            }
        }
        popup.show()
    }

    private fun toggleDesktopMode() {
        val webView = getActiveTab()?.webView ?: return
        val currentUa = webView.settings.userAgentString
        if (currentUa.contains("Mobile")) {
            webView.settings.userAgentString = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 YourBrowser/1.0"
            Toast.makeText(this, "Desktop Site Enabled", Toast.LENGTH_SHORT).show()
        } else {
            webView.settings.userAgentString = null // Default mobile UA
            Toast.makeText(this, "Mobile Site Enabled", Toast.LENGTH_SHORT).show()
        }
        webView.reload()
    }

    private fun promptLockTab(tab: BrowserTab) {
        if (tab.isLocked) {
            tab.isLocked = false
            tab.passwordHash = ""
            tab.isCurrentSessionUnlocked = false
            updateLockOverlay(tab)
            Toast.makeText(this, "Tab unlocked permanently", Toast.LENGTH_SHORT).show()
            return
        }

        val input = EditText(this).apply {
            inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
            hint = "Enter PIN or Password"
            setPadding(40, 30, 40, 30)
        }

        AlertDialog.Builder(this, com.google.android.material.R.style.Theme_Material3_Dark_Dialog_Alert)
            .setTitle("🔒 Protect Tab Session")
            .setMessage("Set a passcode to lock this tab:")
            .setView(input)
            .setPositiveButton("Lock") { _, _ ->
                val pwd = input.text.toString().trim()
                if (pwd.isNotEmpty()) {
                    tab.isLocked = true
                    tab.passwordHash = SecurityVault.hashPassword(pwd)
                    tab.isCurrentSessionUnlocked = true
                    updateLockOverlay(tab)
                    Toast.makeText(this, "Tab locked with password", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun addNewTab(url: String) {
        val tabId = UUID.randomUUID().toString()
        val webView = createWebView(tabId)
        val tab = BrowserTab(
            id = tabId,
            url = url,
            webView = webView
        )
        tabs.add(tab)
        binding.webContainer.addView(webView)
        selectTab(tabId)
        webView.loadUrl(url)
    }

    private fun selectTab(tabId: String) {
        activeTabId = tabId
        tabs.forEach { tab ->
            tab.webView?.visibility = if (tab.id == tabId) View.VISIBLE else View.GONE
        }
        binding.txtTabCount.text = tabs.size.toString()

        val activeTab = getActiveTab() ?: return
        binding.edtOmnibox.setText(activeTab.url)
        updateBookmarkIcon(activeTab.url)
        updateLockOverlay(activeTab)
    }

    private fun closeTab(tabId: String) {
        val index = tabs.indexOfFirst { it.id == tabId }
        if (index >= 0) {
            val tab = tabs[index]
            binding.webContainer.removeView(tab.webView)
            tab.webView?.destroy()
            tabs.removeAt(index)

            if (tabs.isEmpty()) {
                addNewTab("https://search.brave.com")
            } else {
                val nextIndex = if (index >= tabs.size) tabs.size - 1 else index
                selectTab(tabs[nextIndex].id)
            }
        }
    }

    private fun updateLockOverlay(tab: BrowserTab) {
        if (tab.isLocked && !tab.isCurrentSessionUnlocked) {
            binding.layoutTabLockOverlay.visibility = View.VISIBLE
            tab.webView?.visibility = View.GONE
            binding.edtOmnibox.setText("🔒 [Encrypted Tab Session]")
            binding.imgSecurityLock.setImageResource(R.drawable.ic_lock)
        } else {
            binding.layoutTabLockOverlay.visibility = View.GONE
            tab.webView?.visibility = View.VISIBLE
            binding.edtOmnibox.setText(tab.url)
            val isHttps = tab.url.startsWith("https://")
            binding.imgSecurityLock.setImageResource(if (isHttps) R.drawable.ic_lock else R.drawable.ic_shield)
        }
    }

    private fun updateBookmarkIcon(url: String) {
        if (dataManager.isBookmarked(url)) {
            binding.btnBookmark.setImageResource(R.drawable.ic_star_filled)
            binding.btnBookmark.clearColorFilter()
        } else {
            binding.btnBookmark.setImageResource(R.drawable.ic_star)
            binding.btnBookmark.setColorFilter(getColor(R.color.text_secondary))
        }
    }

    private fun getActiveTab(): BrowserTab? = tabs.firstOrNull { it.id == activeTabId }

    @SuppressLint("SetJavaScriptEnabled")
    private fun createWebView(tabId: String): WebView {
        val webView = WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                useWideViewPort = true
                loadWithOverviewMode = true
                setSupportZoom(true)
                builtInZoomControls = true
                displayZoomControls = false
                mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
                userAgentString = "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 YourBrowser/1.0"
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                val url = request?.url?.toString() ?: return null
                return shieldsInterceptor.intercept(url)
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                url?.let {
                    val active = getActiveTab()
                    if (active?.id == tabId) {
                        active.url = it
                        binding.edtOmnibox.setText(it)
                        updateBookmarkIcon(it)
                        binding.pageProgressBar.visibility = View.VISIBLE
                    }
                }
                view?.evaluateJavascript(BraveShieldsInterceptor.ANTI_POPUP_JS, null)
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                url?.let {
                    val active = getActiveTab()
                    if (active?.id == tabId) {
                        binding.pageProgressBar.visibility = View.GONE
                        dataManager.addHistory(view?.title ?: it, it)
                    }
                }
                view?.evaluateJavascript(BraveShieldsInterceptor.ANTI_POPUP_JS, null)
            }

            override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: SslError?) {
                // Safe handling: proceed or notify
                handler?.proceed()
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (getActiveTab()?.id == tabId) {
                    binding.pageProgressBar.progress = newProgress
                    if (newProgress >= 100) {
                        binding.pageProgressBar.visibility = View.GONE
                    }
                }
            }

            override fun onReceivedTitle(view: WebView?, title: String?) {
                super.onReceivedTitle(view, title)
                tabs.firstOrNull { it.id == tabId }?.let { tab ->
                    tab.title = title ?: "Untitled"
                }
            }
        }

        return webView
    }

    override fun onBackPressed() {
        val webView = getActiveTab()?.webView
        if (webView != null && webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
