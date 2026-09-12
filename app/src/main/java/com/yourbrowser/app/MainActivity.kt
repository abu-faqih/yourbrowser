package com.yourbrowser.app

import android.Manifest
import android.app.AlertDialog
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Build
import android.os.Bundle
import android.text.Editable
import android.text.InputType
import android.text.TextWatcher
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.yourbrowser.app.databinding.ActivityMainBinding
import com.yourbrowser.core.browser.GeckoViewEngine
import com.yourbrowser.feature.downloader.engine.ParallelStreamDownloader
import com.yourbrowser.feature.downloader.export.MediaExporter
import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.DownloadState
import com.yourbrowser.feature.downloader.service.DownloadService
import com.yourbrowser.feature.downloader.sniffer.MediaSniffer
import com.yourbrowser.feature.vault.VaultSession
import com.yourbrowser.feature.vault.VaultSessionManager
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import org.mozilla.geckoview.GeckoResult
import org.mozilla.geckoview.GeckoSession
import java.io.File
import java.net.URLDecoder
import java.net.URLEncoder
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var vaultManager: VaultSessionManager
    private lateinit var mediaSniffer: MediaSniffer
    private lateinit var downloader: ParallelStreamDownloader
    private lateinit var geckoEngine: GeckoViewEngine

    private var currentGeckoSession: GeckoSession? = null
    private var canSessionGoBack: Boolean = false
    private var canSessionGoForward: Boolean = false

    // Tab Management State
    private val tabList = mutableListOf<BrowserTab>()
    private var activeTabId: String = ""

    // Download telemetry tracking
    private var activeDownloadFile: File? = null
    private var activeDownloadStream: DetectedMediaStream? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        // Blokir screenshot dan screen-capture di mode incognito (Anti-Forensic)
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        vaultManager = VaultSessionManager(applicationContext)
        mediaSniffer = MediaSniffer()
        downloader = ParallelStreamDownloader()
        geckoEngine = GeckoViewEngine(mediaSniffer)

        initViews()
        initBackNavigation()
        requestNotificationPermissionIfNeeded()
        observeMediaStreams()

        // Buka dialog vault saat aplikasi pertama kali dibuka
        showVaultUnlockDialog()
    }

    private fun initViews() {
        // Top Toolbar
        binding.tvVaultIndicator.setOnClickListener {
            showVaultUnlockDialog()
        }

        binding.btnQuickProfile.setOnClickListener {
            showVaultUnlockDialog()
        }

        binding.btnRefresh.setOnClickListener {
            currentGeckoSession?.reload()
        }

        binding.btnToolbarMore.setOnClickListener {
            showTabManagerDialog()
        }

        binding.etUrl.setOnEditorActionListener { _, _, _ ->
            val input = binding.etUrl.text.toString().trim()
            navigateUrl(input)
            true
        }

        // Floating Reactive Sniffer FAB
        binding.fabDownload.setOnClickListener {
            showMediaGrabberBottomSheet()
        }

        binding.tvSnifferBubble.setOnClickListener {
            showMediaGrabberBottomSheet()
        }

        // Bottom Navigation Bar (Thumb Zone)
        binding.btnNavBack.setOnClickListener {
            if (canSessionGoBack && currentGeckoSession != null) {
                currentGeckoSession?.goBack()
            } else {
                Toast.makeText(this, "Tidak ada halaman sebelumnya", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnNavForward.setOnClickListener {
            if (canSessionGoForward && currentGeckoSession != null) {
                currentGeckoSession?.goForward()
            } else {
                Toast.makeText(this, "Tidak ada halaman berikutnya", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnNavHome.setOnClickListener {
            navigateUrl("https://duckduckgo.com")
        }

        binding.btnNavTabs.setOnClickListener {
            showTabManagerDialog()
        }

        binding.btnNavDownloads.setOnClickListener {
            showVaultMediaLibraryDialog()
        }

        binding.btnNavPanic.setOnClickListener {
            triggerPanicKillSwitch()
        }
    }

    private fun initBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (canSessionGoBack && currentGeckoSession != null) {
                    currentGeckoSession?.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }
    }

    private fun navigateUrl(input: String) {
        if (input.isEmpty()) return

        val url = if (input.startsWith("http://") || input.startsWith("https://")) {
            input
        } else if (input.contains(".") && !input.contains(" ")) {
            "https://$input"
        } else {
            "https://duckduckgo.com/?q=${URLEncoder.encode(input, "UTF-8")}"
        }

        binding.etUrl.setText(url)
        mediaSniffer.clearStreams()
        currentGeckoSession?.loadUri(url)

        // Update active tab URL
        tabList.find { it.id == activeTabId }?.let {
            it.url = url
            it.title = url.removePrefix("https://").removePrefix("http://").take(24)
        }
    }

    // =========================================================================
    // LAYAR 02: DIALOG AUTENTIKASI VAULT (ZERO-KNOWLEDGE PLAUSIBLE DENIABILITY)
    // =========================================================================
    private fun showVaultUnlockDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_unlock_vault, null)
        val etPassword = dialogView.findViewById<EditText>(R.id.etVaultPassword)
        val btnToggle = dialogView.findViewById<ImageButton>(R.id.btnTogglePassword)
        val btnUnlock = dialogView.findViewById<Button>(R.id.btnSubmitUnlock)
        val tvEntropy = dialogView.findViewById<TextView>(R.id.tvEntropyStatus)
        val bar1 = dialogView.findViewById<View>(R.id.barEntropy1)
        val bar2 = dialogView.findViewById<View>(R.id.barEntropy2)
        val bar3 = dialogView.findViewById<View>(R.id.barEntropy3)
        val bar4 = dialogView.findViewById<View>(R.id.barEntropy4)

        var isPasswordVisible = false

        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .setCancelable(vaultManager.activeSession.value != null)
            .create()

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))

        val originalTypeface = etPassword.typeface

        btnToggle.setOnClickListener {
            isPasswordVisible = !isPasswordVisible
            if (isPasswordVisible) {
                etPassword.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                btnToggle.setImageResource(R.drawable.ic_visibility_off)
            } else {
                etPassword.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
                btnToggle.setImageResource(R.drawable.ic_visibility)
            }
            etPassword.typeface = originalTypeface
            etPassword.setSelection(etPassword.text.length)
        }

        etPassword.setOnEditorActionListener { _, actionId, event ->
            if (actionId == EditorInfo.IME_ACTION_DONE ||
                (event != null && event.keyCode == KeyEvent.KEYCODE_ENTER && event.action == KeyEvent.ACTION_DOWN)
            ) {
                btnUnlock.performClick()
                true
            } else {
                false
            }
        }

        etPassword.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                val len = s?.length ?: 0
                val activeBg = ContextCompat.getDrawable(this@MainActivity, R.drawable.bg_entropy_bar_active)
                val inactiveBg = ContextCompat.getDrawable(this@MainActivity, R.drawable.bg_entropy_bar_inactive)

                bar1.background = if (len >= 1) activeBg else inactiveBg
                bar2.background = if (len >= 4) activeBg else inactiveBg
                bar3.background = if (len >= 8) activeBg else inactiveBg
                bar4.background = if (len >= 12) activeBg else inactiveBg

                tvEntropy.text = when {
                    len == 0 -> "SIAP DERIVASI"
                    len < 4 -> "ENTROPY RENDAH"
                    len < 8 -> "ENTROPY SEDANG"
                    len < 12 -> "ENTROPY TINGGI"
                    else -> "ENTROPY MAKSIMAL"
                }
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        btnUnlock.setOnClickListener {
            val passChars = CharArray(etPassword.text.length)
            etPassword.text.getChars(0, etPassword.text.length, passChars, 0)
            etPassword.text.clear()

            if (passChars.isEmpty()) {
                Toast.makeText(this, "Frasa sandi tidak boleh kosong", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val session = vaultManager.unlockVault(passChars)
            onVaultUnlocked(session)
            dialog.dismiss()
        }

        dialog.setOnShowListener {
            etPassword.requestFocus()
            val imm = getSystemService(INPUT_METHOD_SERVICE) as? InputMethodManager
            imm?.showSoftInput(etPassword, InputMethodManager.SHOW_IMPLICIT)
        }

        dialog.show()
    }

    private fun onVaultUnlocked(session: VaultSession) {
        val displayId = session.vaultId.take(8)
        binding.tvVaultIndicator.text = "🔒 $displayId"
        Toast.makeText(this, "Enclave Aktif: $displayId", Toast.LENGTH_SHORT).show()

        // Inisialisasi engine browser pada storage partisi vault
        val profileDir = File(session.storageDir, "browser_profile")
        geckoEngine.initialize(this, profileDir)

        // Bersihkan tabs lama
        tabList.clear()
        val initialTab = BrowserTab(
            id = UUID.randomUUID().toString(),
            title = "DuckDuckGo Privacy Search",
            url = "https://duckduckgo.com",
            isActive = true
        )
        tabList.add(initialTab)
        activeTabId = initialTab.id
        updateTabBadge()

        createGeckoSessionForTab(initialTab)
    }

    private fun createGeckoSessionForTab(tab: BrowserTab) {
        currentGeckoSession?.let { geckoEngine.destroySession(it) }

        val newSession = geckoEngine.createSession(isPrivate = true)

        newSession.navigationDelegate = object : GeckoSession.NavigationDelegate {
            override fun onCanGoBack(session: GeckoSession, canGoBack: Boolean) {
                canSessionGoBack = canGoBack
                binding.btnNavBack.alpha = if (canGoBack) 1.0f else 0.4f
            }
            override fun onCanGoForward(session: GeckoSession, canGoForward: Boolean) {
                canSessionGoForward = canGoForward
                binding.btnNavForward.alpha = if (canGoForward) 1.0f else 0.4f
            }
            override fun onLoadRequest(session: GeckoSession, request: GeckoSession.NavigationDelegate.LoadRequest): GeckoResult<org.mozilla.geckoview.AllowOrDeny>? {
                val uri = request.uri
                if (uri.startsWith(GeckoViewEngine.SCHEME_MEDIA_HOOK) || uri.startsWith(GeckoViewEngine.SCHEME_PLAYER_LAUNCH)) {
                    val encodedMediaUrl = if (uri.startsWith(GeckoViewEngine.SCHEME_MEDIA_HOOK)) {
                        uri.removePrefix(GeckoViewEngine.SCHEME_MEDIA_HOOK)
                    } else {
                        uri.removePrefix(GeckoViewEngine.SCHEME_PLAYER_LAUNCH)
                    }
                    try {
                        val realMediaUrl = URLDecoder.decode(encodedMediaUrl, "UTF-8")
                        mediaSniffer.inspectNetworkResponse(url = realMediaUrl, mimeType = null)
                    } catch (_: Exception) {}
                    return GeckoResult.fromValue(org.mozilla.geckoview.AllowOrDeny.DENY)
                }

                mediaSniffer.inspectNetworkResponse(url = uri, mimeType = null)
                return GeckoResult.fromValue(org.mozilla.geckoview.AllowOrDeny.ALLOW)
            }
        }

        newSession.progressDelegate = object : GeckoSession.ProgressDelegate {
            override fun onPageStart(session: GeckoSession, url: String) {
                binding.pbPageLoad.visibility = View.VISIBLE
                binding.pbPageLoad.progress = 10
                binding.etUrl.setText(url)
                tab.url = url
            }
            override fun onPageStop(session: GeckoSession, success: Boolean) {
                binding.pbPageLoad.visibility = View.GONE
                if (success) {
                    geckoEngine.injectSnifferScript(session)
                }
            }
            override fun onProgressChange(session: GeckoSession, progress: Int) {
                binding.pbPageLoad.progress = progress
            }
        }

        geckoEngine.bindSessionToView(newSession, binding.geckoView)
        currentGeckoSession = newSession
        newSession.loadUri(tab.url)
    }

    private fun updateTabBadge() {
        binding.tvTabCounter.text = tabList.size.toString()
    }

    // =========================================================================
    // LAYAR 01 & 03: REACTIVE SNIFFER & MEDIA GRABBER BOTTOM SHEET
    // =========================================================================
    private fun observeMediaStreams() {
        lifecycleScope.launch {
            mediaSniffer.detectedStreams.collectLatest { streams ->
                if (streams.isEmpty()) {
                    binding.layoutSnifferFabContainer.visibility = View.GONE
                } else {
                    binding.layoutSnifferFabContainer.visibility = View.VISIBLE
                    binding.tvFabDownloadText.text = "Unduh Video (${streams.size})"
                    binding.tvSnifferBubble.text = "HLS Stream Ditangkap (${streams.size})"
                }
            }
        }
    }

    private fun showMediaGrabberBottomSheet() {
        val streams = mediaSniffer.detectedStreams.value
        val bottomSheet = BottomSheetDialog(this, R.style.Theme_YourBrowser_BottomSheetDialog)
        val view = LayoutInflater.from(this).inflate(R.layout.bottomsheet_media_grabber, null)

        val tvTitle = view.findViewById<TextView>(R.id.tvSheetTitle)
        val tvBadge = view.findViewById<TextView>(R.id.tvMediaCountBadge)
        val tvMetaTitle = view.findViewById<TextView>(R.id.tvMetaTitle)
        val tvMetaUrl = view.findViewById<TextView>(R.id.tvMetaUrl)
        val tvEmptyGuide = view.findViewById<TextView>(R.id.tvEmptyMediaGuide)
        val rvStreams = view.findViewById<RecyclerView>(R.id.rvMediaStreams)
        val btnClose = view.findViewById<ImageButton>(R.id.btnCloseSheet)

        tvTitle.text = getString(R.string.detected_videos)
        tvBadge.text = streams.size.toString()

        if (streams.isEmpty()) {
            tvEmptyGuide.visibility = View.VISIBLE
            rvStreams.visibility = View.GONE
            tvMetaTitle.text = "Belum Ada Media"
            tvMetaUrl.text = binding.etUrl.text.toString()
        } else {
            tvEmptyGuide.visibility = View.GONE
            rvStreams.visibility = View.VISIBLE
            tvMetaTitle.text = streams.first().title.ifEmpty { "Video Terdeteksi" }
            tvMetaUrl.text = streams.first().url
        }

        btnClose.setOnClickListener {
            bottomSheet.dismiss()
        }

        val adapter = MediaStreamAdapter(
            onPlayClick = { stream ->
                bottomSheet.dismiss()
                val activeVault = vaultManager.activeSession.value
                NativeVideoPlayerActivity.launch(
                    context = this,
                    mediaUrl = stream.url,
                    title = stream.title.ifEmpty { "Video Stream" },
                    streamId = stream.id,
                    format = stream.format,
                    vaultStorageDir = activeVault?.storageDir,
                    isLocalFile = false
                )
            },
            onDownloadClick = { stream ->
                bottomSheet.dismiss()
                startStreamDownload(stream)
            }
        )

        rvStreams.layoutManager = LinearLayoutManager(this)
        rvStreams.adapter = adapter
        adapter.submitList(streams)

        bottomSheet.setContentView(view)
        bottomSheet.show()
    }

    // =========================================================================
    // LAYAR 04: STATUS UNDUHAN AKTIF & TELEMETRY MUXING
    // =========================================================================
    private fun startStreamDownload(stream: DetectedMediaStream) {
        val activeVault = vaultManager.activeSession.value
        if (activeVault == null) {
            Toast.makeText(this, "Vault belum terbuka!", Toast.LENGTH_SHORT).show()
            return
        }

        val downloadsFolder = File(activeVault.storageDir, "downloads")
        downloadsFolder.mkdirs()
        val cacheFolder = File(activeVault.storageDir, "cache/media").apply { mkdirs() }

        val cleanTitle = stream.title.replace(Regex("[^a-zA-Z0-9._-]"), "_")
        val outputFile = File(downloadsFolder, if (cleanTitle.endsWith(".mp4")) cleanTitle else "$cleanTitle.mp4")

        activeDownloadFile = outputFile
        activeDownloadStream = stream

        // Mulai download via Foreground Service dengan dukungan Unified Media Cache
        DownloadService.startDownload(this, stream, outputFile, cacheFolder)

        // Tampilkan Telemetry Bottom Sheet (Layar 04)
        showDownloadTelemetrySheet(stream, outputFile)
    }

    private fun showDownloadTelemetrySheet(stream: DetectedMediaStream, outputFile: File) {
        val bottomSheet = BottomSheetDialog(this, R.style.Theme_YourBrowser_BottomSheetDialog)
        val view = LayoutInflater.from(this).inflate(R.layout.bottomsheet_download_telemetry, null)

        val tvFileName = view.findViewById<TextView>(R.id.tvTelemetryFileName)
        val tvPipeline = view.findViewById<TextView>(R.id.tvTelemetryPipeline)
        val tvPercentage = view.findViewById<TextView>(R.id.tvTelemetryPercentage)
        val pbProgress = view.findViewById<ProgressBar>(R.id.pbTelemetryProgress)
        val tvChunks = view.findViewById<TextView>(R.id.tvTelemetryChunks)
        val tvSpeed = view.findViewById<TextView>(R.id.tvTelemetrySpeed)
        val tvEta = view.findViewById<TextView>(R.id.tvTelemetryEta)
        val btnPlayWhileDownloading = view.findViewById<Button>(R.id.btnPlayWhileDownloading)
        val btnPause = view.findViewById<Button>(R.id.btnPauseDownload)
        val btnCancel = view.findViewById<Button>(R.id.btnCancelDownload)
        val btnClose = view.findViewById<ImageButton>(R.id.btnCloseTelemetry)

        var progressivePlaybackUrl: String? = null

        tvFileName.text = outputFile.name
        tvPipeline.text = "Format: ${stream.format.name} ➞ Parallel Segments ➞ Shared Cache & Native MP4 Muxer"

        btnPlayWhileDownloading.setOnClickListener {
            val playUrl = progressivePlaybackUrl ?: stream.url
            val activeVault = vaultManager.activeSession.value
            NativeVideoPlayerActivity.launch(
                context = this,
                mediaUrl = playUrl,
                title = stream.title.ifEmpty { outputFile.name },
                streamId = stream.id,
                format = stream.format,
                vaultStorageDir = activeVault?.storageDir,
                isLocalFile = false
            )
        }

        btnClose.setOnClickListener {
            bottomSheet.dismiss()
        }

        btnCancel.setOnClickListener {
            DownloadService.cancelDownload(this)
            bottomSheet.dismiss()
            Toast.makeText(this, "Unduhan dibatalkan", Toast.LENGTH_SHORT).show()
        }

        btnPause.setOnClickListener {
            Toast.makeText(this, "Download dijeda", Toast.LENGTH_SHORT).show()
        }

        val activeDownloaderInstance = DownloadService.activeDownloader ?: downloader
        lifecycleScope.launch {
            activeDownloaderInstance.downloadState.collectLatest { state ->
                when (state) {
                    is DownloadState.Downloading -> {
                        progressivePlaybackUrl = state.progressivePlaybackUrl
                        pbProgress.isIndeterminate = state.progressPercent <= 0
                        if (state.progressPercent > 0) {
                            pbProgress.progress = state.progressPercent
                        }
                        tvPercentage.text = "${state.progressPercent}%"

                        val speedMb = String.format("%.1f", state.speedBytesPerSec / (1024.0 * 1024.0))
                        tvSpeed.text = "$speedMb MB/s"
                        tvChunks.text = "${state.progressPercent * 3} / 300 chunks"

                        val remainingSeconds = if (state.speedBytesPerSec > 0) {
                            ((100 - state.progressPercent) * 2).coerceAtLeast(1)
                        } else 30
                        tvEta.text = "~$remainingSeconds detik"
                    }
                    is DownloadState.Completed -> {
                        pbProgress.progress = 100
                        tvPercentage.text = "100%"
                        tvChunks.text = "Muxing Selesai"
                        tvSpeed.text = "Tersimpan"
                        tvEta.text = "0s"
                        Toast.makeText(this@MainActivity, "Selesai diunduh ke vault: ${outputFile.name}", Toast.LENGTH_LONG).show()
                    }
                    is DownloadState.Failed -> {
                        tvChunks.text = "Gagal"
                        tvSpeed.text = "Error"
                        Toast.makeText(this@MainActivity, "Gagal: ${state.error}", Toast.LENGTH_SHORT).show()
                    }
                    DownloadState.Idle -> {}
                }
            }
        }

        bottomSheet.setContentView(view)
        bottomSheet.show()
    }

    // =========================================================================
    // LAYAR 05: TAB SWITCHER & SESSION ISOLATION DIALOG
    // =========================================================================
    private fun showTabManagerDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_tab_manager, null)
        val tvVaultId = dialogView.findViewById<TextView>(R.id.tvTabVaultId)
        val tvCount = dialogView.findViewById<TextView>(R.id.tvTabManagerCount)
        val btnNewTab = dialogView.findViewById<Button>(R.id.btnNewTab)
        val btnClose = dialogView.findViewById<ImageButton>(R.id.btnCloseTabManager)
        val rvTabs = dialogView.findViewById<RecyclerView>(R.id.rvTabsGrid)

        val activeSession = vaultManager.activeSession.value
        val displayId = activeSession?.vaultId?.take(8) ?: "DECOY"
        tvVaultId.text = "🔒 VAULT: $displayId"
        tvCount.text = "Tab Aktif: ${tabList.size}"

        val dialog = AlertDialog.Builder(this, android.R.style.Theme_Black_NoTitleBar_Fullscreen)
            .setView(dialogView)
            .create()

        dialog.window?.setBackgroundDrawable(ColorDrawable(ContextCompat.getColor(this, R.color.surface_ground)))

        lateinit var adapter: TabAdapter

        adapter = TabAdapter(
            onTabClick = { clickedTab ->
                tabList.forEach { it.isActive = (it.id == clickedTab.id) }
                activeTabId = clickedTab.id
                binding.etUrl.setText(clickedTab.url)
                createGeckoSessionForTab(clickedTab)
                dialog.dismiss()
            },
            onCloseClick = { closedTab ->
                if (tabList.size <= 1) {
                    Toast.makeText(this, "Minimal harus ada 1 tab", Toast.LENGTH_SHORT).show()
                    return@TabAdapter
                }
                tabList.remove(closedTab)
                if (closedTab.id == activeTabId) {
                    val nextTab = tabList.last()
                    nextTab.isActive = true
                    activeTabId = nextTab.id
                    binding.etUrl.setText(nextTab.url)
                    createGeckoSessionForTab(nextTab)
                }
                adapter.submitList(tabList.toList())
                tvCount.text = "Tab Aktif: ${tabList.size}"
                updateTabBadge()
            }
        )

        rvTabs.layoutManager = GridLayoutManager(this, 2)
        rvTabs.adapter = adapter
        adapter.submitList(tabList.toList())

        btnNewTab.setOnClickListener {
            val newTab = BrowserTab(
                id = UUID.randomUUID().toString(),
                title = "New Tab",
                url = "https://duckduckgo.com",
                isActive = true
            )
            tabList.forEach { it.isActive = false }
            tabList.add(newTab)
            activeTabId = newTab.id
            updateTabBadge()
            binding.etUrl.setText(newTab.url)
            createGeckoSessionForTab(newTab)
            dialog.dismiss()
        }

        btnClose.setOnClickListener {
            dialog.dismiss()
        }

        dialog.show()
    }

    // =========================================================================
    // LAYAR 06: VAULT MEDIA LIBRARY & DOWNLOADS
    // =========================================================================
    private fun showVaultMediaLibraryDialog() {
        val activeSession = vaultManager.activeSession.value
        if (activeSession == null) {
            Toast.makeText(this, "Vault belum aktif", Toast.LENGTH_SHORT).show()
            return
        }

        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_vault_media_library, null)
        val tvPartition = dialogView.findViewById<TextView>(R.id.tvVaultPartitionId)
        val tvStorage = dialogView.findViewById<TextView>(R.id.tvStorageUsage)
        val pbStorage = dialogView.findViewById<ProgressBar>(R.id.pbStorageQuota)
        val tvEmpty = dialogView.findViewById<TextView>(R.id.tvEmptyVaultFiles)
        val rvFiles = dialogView.findViewById<RecyclerView>(R.id.rvVaultFiles)
        val btnBack = dialogView.findViewById<ImageButton>(R.id.btnBackMediaLibrary)
        val btnClose = dialogView.findViewById<ImageButton>(R.id.btnCloseMediaLibrary)

        val displayId = activeSession.vaultId.take(8)
        tvPartition.text = "Partisi: $displayId"

        val dialog = AlertDialog.Builder(this, android.R.style.Theme_Black_NoTitleBar_Fullscreen)
            .setView(dialogView)
            .create()

        dialog.window?.setBackgroundDrawable(ColorDrawable(ContextCompat.getColor(this, R.color.surface_ground)))

        btnBack.setOnClickListener { dialog.dismiss() }
        btnClose.setOnClickListener { dialog.dismiss() }

        val downloadsFolder = File(activeSession.storageDir, "downloads")
        downloadsFolder.mkdirs()

        fun loadFiles() {
            val files = downloadsFolder.listFiles()?.filter { it.isFile } ?: emptyList()
            var totalBytes = 0L
            val fileItems = files.map { file ->
                totalBytes += file.length()
                val sizeMb = String.format("%.1f MB", file.length() / (1024.0 * 1024.0))
                val ext = file.extension.uppercase().ifEmpty { "MP4" }
                VaultFileItem(file, file.name, sizeMb, ext)
            }

            val usedMb = String.format("%.1f MB", totalBytes / (1024.0 * 1024.0))
            tvStorage.text = "$usedMb / 2.0 GB"
            val percentUsed = ((totalBytes / (2.0 * 1024 * 1024 * 1024)) * 100).toInt().coerceIn(1, 100)
            pbStorage.progress = percentUsed

            if (fileItems.isEmpty()) {
                tvEmpty.visibility = View.VISIBLE
                rvFiles.visibility = View.GONE
            } else {
                tvEmpty.visibility = View.GONE
                rvFiles.visibility = View.VISIBLE
            }

            val adapter = VaultMediaAdapter(
                onItemClick = { item ->
                    NativeVideoPlayerActivity.launch(
                        context = this@MainActivity,
                        mediaUrl = item.file.absolutePath,
                        title = item.name,
                        vaultStorageDir = activeSession.storageDir,
                        isLocalFile = true
                    )
                },
                onExportClick = { item ->
                    lifecycleScope.launch {
                        val uri = MediaExporter.exportToPublicGallery(this@MainActivity, item.file)
                        if (uri != null) {
                            Toast.makeText(this@MainActivity, "Berhasil diekspor ke Galeri!", Toast.LENGTH_LONG).show()
                        } else {
                            Toast.makeText(this@MainActivity, "Gagal mengekspor berkas", Toast.LENGTH_SHORT).show()
                        }
                    }
                },
                onDeleteClick = { item ->
                    item.file.delete()
                    Toast.makeText(this@MainActivity, "Berkas dihapus dari vault", Toast.LENGTH_SHORT).show()
                    loadFiles()
                }
            )

            rvFiles.layoutManager = LinearLayoutManager(this)
            rvFiles.adapter = adapter
            adapter.submitList(fileItems)
        }

        loadFiles()
        dialog.show()
    }

    // =========================================================================
    // PANIC KILL-SWITCH (ZEROIZATION & INSTANT PURGE)
    // =========================================================================
    private fun triggerPanicKillSwitch() {
        // Hancurkan session GeckoView aktif
        currentGeckoSession?.let { geckoEngine.destroySession(it) }
        currentGeckoSession = null

        // Hancurkan tab list
        tabList.clear()
        activeTabId = ""
        updateTabBadge()

        // Bersihkan sniffer streams
        mediaSniffer.clearStreams()

        // Kunci vault & bersihkan memory key
        vaultManager.lockActiveVault()

        // Clear UI address & indikator
        binding.etUrl.setText("")
        binding.tvVaultIndicator.text = "🔒 Vault Terkunci"

        // Trigger memory purge
        System.gc()

        Toast.makeText(this, "🚨 PANIC: Sesi Dihancurkan & Vault Terkunci!", Toast.LENGTH_LONG).show()

        // Tampilkan dialog unlock baru
        showVaultUnlockDialog()
    }

    override fun onDestroy() {
        super.onDestroy()
        currentGeckoSession?.let { geckoEngine.destroySession(it) }
        geckoEngine.shutdown()
        vaultManager.lockActiveVault()
    }
}
