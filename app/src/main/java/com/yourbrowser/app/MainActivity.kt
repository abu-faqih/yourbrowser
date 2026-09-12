package com.yourbrowser.app

import android.Manifest
import android.app.AlertDialog
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
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
import com.yourbrowser.feature.vault.VaultSessionManager
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import org.mozilla.geckoview.GeckoSession
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var vaultManager: VaultSessionManager
    private lateinit var mediaSniffer: MediaSniffer
    private lateinit var downloader: ParallelStreamDownloader
    private lateinit var geckoEngine: GeckoViewEngine
    private var currentGeckoSession: GeckoSession? = null
    private var canSessionGoBack: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        // Blokir screenshot dan screen-capture di mode incognito
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
        binding.tvVaultIndicator.setOnClickListener {
            showVaultUnlockDialog()
        }

        binding.btnGo.setOnClickListener {
            navigateUrl()
        }

        binding.etUrl.setOnEditorActionListener { _, _, _ ->
            navigateUrl()
            true
        }

        binding.fabDownload.setOnClickListener {
            showMediaGrabberBottomSheet()
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

    private fun navigateUrl() {
        val input = binding.etUrl.text.toString().trim()
        if (input.isEmpty()) return

        val url = if (input.startsWith("http://") || input.startsWith("https://")) {
            input
        } else if (input.contains(".") && !input.contains(" ")) {
            "https://$input"
        } else {
            "https://duckduckgo.com/?q=${java.net.URLEncoder.encode(input, "UTF-8")}"
        }

        binding.etUrl.setText(url)
        mediaSniffer.clearStreams()
        currentGeckoSession?.loadUri(url)
    }

    private fun showVaultUnlockDialog() {
        val dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_unlock_vault, null)
        val etPassword = dialogView.findViewById<EditText>(R.id.etVaultPassword)
        val btnUnlock = dialogView.findViewById<Button>(R.id.btnSubmitUnlock)

        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .setCancelable(vaultManager.activeSession.value != null)
            .create()

        btnUnlock.setOnClickListener {
            val passChars = CharArray(etPassword.text.length)
            etPassword.text.getChars(0, etPassword.text.length, passChars, 0)
            etPassword.text.clear()

            if (passChars.isEmpty()) {
                Toast.makeText(this, "Password tidak boleh kosong", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val session = vaultManager.unlockVault(passChars)
            onVaultUnlocked(session)
            dialog.dismiss()
        }

        dialog.show()
    }

    private fun onVaultUnlocked(session: com.yourbrowser.feature.vault.VaultSession) {
        val displayId = session.vaultId.take(8)
        binding.tvVaultIndicator.text = "🔒 Vault: $displayId"
        Toast.makeText(this, "Vault aktif: $displayId", Toast.LENGTH_SHORT).show()

        // Inisialisasi engine browser pada storage partisi vault
        val profileDir = File(session.storageDir, "browser_profile")
        geckoEngine.initialize(this, profileDir)

        // Hancurkan session lama jika ada
        currentGeckoSession?.let { geckoEngine.destroySession(it) }

        val newSession = geckoEngine.createSession(isPrivate = true)

        // Delegate listener untuk history back navigation
        newSession.navigationDelegate = object : GeckoSession.NavigationDelegate {
            override fun onCanGoBack(session: GeckoSession, canGoBack: Boolean) {
                canSessionGoBack = canGoBack
            }
            override fun onCanGoForward(session: GeckoSession, canGoForward: Boolean) {}
            override fun onLoadRequest(session: GeckoSession, request: GeckoSession.NavigationDelegate.LoadRequest): org.mozilla.geckoview.GeckoResult<org.mozilla.geckoview.AllowOrDeny>? {
                mediaSniffer.inspectNetworkResponse(url = request.uri, mimeType = null)
                return org.mozilla.geckoview.GeckoResult.fromValue(org.mozilla.geckoview.AllowOrDeny.ALLOW)
            }
        }

        geckoEngine.bindSessionToView(newSession, binding.geckoView)
        currentGeckoSession = newSession

        // Muat homepage default
        newSession.loadUri("https://duckduckgo.com")
    }

    private fun observeMediaStreams() {
        lifecycleScope.launch {
            mediaSniffer.detectedStreams.collectLatest { streams ->
                if (streams.isEmpty()) {
                    binding.fabDownload.visibility = View.GONE
                } else {
                    binding.fabDownload.visibility = View.VISIBLE
                    binding.fabDownload.text = "⚡ Unduh (${streams.size})"
                }
            }
        }
    }

    private fun showMediaGrabberBottomSheet() {
        val streams = mediaSniffer.detectedStreams.value
        val bottomSheet = BottomSheetDialog(this)
        val view = LayoutInflater.from(this).inflate(R.layout.bottomsheet_media_grabber, null)

        val tvTitle = view.findViewById<TextView>(R.id.tvSheetTitle)
        val rvStreams = view.findViewById<RecyclerView>(R.id.rvMediaStreams)
        val pbDownload = view.findViewById<ProgressBar>(R.id.pbDownloadProgress)
        val tvStatus = view.findViewById<TextView>(R.id.tvDownloadStatus)
        val btnExport = view.findViewById<Button>(R.id.btnExportGallery)

        tvTitle.text = getString(R.string.detected_videos, streams.size)

        var lastDownloadedFile: File? = null

        val adapter = MediaStreamAdapter { stream ->
            lastDownloadedFile = startStreamDownload(stream, pbDownload, tvStatus, btnExport)
        }
        rvStreams.layoutManager = LinearLayoutManager(this)
        rvStreams.adapter = adapter
        adapter.submitList(streams)

        btnExport.setOnClickListener {
            val fileToExport = lastDownloadedFile
            if (fileToExport != null && fileToExport.exists()) {
                lifecycleScope.launch {
                    val uri = MediaExporter.exportToPublicGallery(this@MainActivity, fileToExport)
                    if (uri != null) {
                        Toast.makeText(this@MainActivity, "Berhasil diekspor ke Galeri!", Toast.LENGTH_LONG).show()
                    } else {
                        Toast.makeText(this@MainActivity, "Gagal mengekspor video", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        bottomSheet.setContentView(view)
        bottomSheet.show()
    }

    private fun startStreamDownload(
        stream: DetectedMediaStream,
        progressBar: ProgressBar,
        statusText: TextView,
        exportButton: Button
    ): File? {
        val activeVault = vaultManager.activeSession.value
        if (activeVault == null) {
            Toast.makeText(this, "Vault belum terbuka!", Toast.LENGTH_SHORT).show()
            return null
        }

        val downloadsFolder = File(activeVault.storageDir, "downloads")
        val cleanTitle = stream.title.replace(Regex("[^a-zA-Z0-9._-]"), "_")
        val outputFile = File(downloadsFolder, if (cleanTitle.endsWith(".mp4")) cleanTitle else "$cleanTitle.mp4")

        progressBar.visibility = View.VISIBLE
        statusText.visibility = View.VISIBLE
        exportButton.visibility = View.GONE

        // Mulai download via Foreground Service untuk kehandalan di background
        DownloadService.startDownload(this, stream, outputFile)

        lifecycleScope.launch {
            downloader.downloadState.collectLatest { state ->
                when (state) {
                    is DownloadState.Downloading -> {
                        progressBar.isIndeterminate = state.progressPercent <= 0
                        if (state.progressPercent > 0) {
                            progressBar.progress = state.progressPercent
                        }
                        val speedKb = state.speedBytesPerSec / 1024
                        statusText.text = "Mengunduh: ${state.progressPercent}% (${speedKb} KB/s)"
                    }
                    is DownloadState.Completed -> {
                        progressBar.visibility = View.GONE
                        statusText.text = "Selesai diunduh ke vault!"
                        exportButton.visibility = View.VISIBLE
                        Toast.makeText(this@MainActivity, "Tersimpan di vault: ${outputFile.name}", Toast.LENGTH_LONG).show()
                    }
                    is DownloadState.Failed -> {
                        progressBar.visibility = View.GONE
                        statusText.text = "Gagal: ${state.error}"
                        Toast.makeText(this@MainActivity, "Gagal: ${state.error}", Toast.LENGTH_SHORT).show()
                    }
                    DownloadState.Idle -> {}
                }
            }
        }
        return outputFile
    }

    override fun onDestroy() {
        super.onDestroy()
        currentGeckoSession?.let { geckoEngine.destroySession(it) }
        geckoEngine.shutdown()
        vaultManager.lockActiveVault()
    }
}
