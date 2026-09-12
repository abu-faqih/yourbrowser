package com.yourbrowser.app

import android.app.PictureInPictureParams
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.media.AudioManager
import android.media.PlaybackParams
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Rational
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.SeekBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.yourbrowser.app.databinding.ActivityNativePlayerBinding
import com.yourbrowser.feature.downloader.cache.LocalStreamingProxy
import com.yourbrowser.feature.downloader.cache.MediaCacheManager
import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.DownloadState
import com.yourbrowser.feature.downloader.model.StreamFormat
import com.yourbrowser.feature.downloader.service.DownloadService
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.io.File
import kotlin.math.abs

class NativeVideoPlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityNativePlayerBinding
    private lateinit var audioManager: AudioManager

    private var videoUri: Uri? = null
    private var videoTitle: String = "Video"
    private var streamUrl: String = ""
    private var streamId: String = ""
    private var streamFormatStr: String = StreamFormat.DIRECT_MP4.name
    private var vaultStorageDirPath: String? = null
    private var isLocalFile: Boolean = false

    private val handler = Handler(Looper.getMainLooper())
    private var isControlsVisible = true
    private var isUserSeeking = false
    private var currentSpeedIndex = 1
    private val speedOptions = floatArrayOf(0.75f, 1.0f, 1.25f, 1.5f, 2.0f)

    // Gesture control state
    private var touchStartX = 0f
    private var touchStartY = 0f
    private var initialVolume = 0
    private var maxVolume = 1
    private var initialBrightness = 0.5f

    companion object {
        const val EXTRA_MEDIA_URL = "extra_media_url"
        const val EXTRA_MEDIA_TITLE = "extra_media_title"
        const val EXTRA_STREAM_ID = "extra_stream_id"
        const val EXTRA_STREAM_FORMAT = "extra_stream_format"
        const val EXTRA_VAULT_DIR = "extra_vault_dir"
        const val EXTRA_IS_LOCAL_FILE = "extra_is_local_file"

        fun launch(
            context: Context,
            mediaUrl: String,
            title: String,
            streamId: String = "",
            format: StreamFormat = StreamFormat.DIRECT_MP4,
            vaultStorageDir: File? = null,
            isLocalFile: Boolean = false
        ) {
            val intent = Intent(context, NativeVideoPlayerActivity::class.java).apply {
                putExtra(EXTRA_MEDIA_URL, mediaUrl)
                putExtra(EXTRA_MEDIA_TITLE, title)
                putExtra(EXTRA_STREAM_ID, streamId)
                putExtra(EXTRA_STREAM_FORMAT, format.name)
                putExtra(EXTRA_VAULT_DIR, vaultStorageDir?.absolutePath)
                putExtra(EXTRA_IS_LOCAL_FILE, isLocalFile)
            }
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Enforce anti-forensic screen protection
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        super.onCreate(savedInstanceState)
        binding = ActivityNativePlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
        maxVolume = audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC).coerceAtLeast(1)

        parseIntentExtras()
        initViews()
        initPlayback()
        setupGestureDetector()
        observeActiveDownload()
    }

    private fun parseIntentExtras() {
        streamUrl = intent.getStringExtra(EXTRA_MEDIA_URL) ?: ""
        videoTitle = intent.getStringExtra(EXTRA_MEDIA_TITLE) ?: "Streaming Media"
        streamId = intent.getStringExtra(EXTRA_STREAM_ID) ?: ""
        streamFormatStr = intent.getStringExtra(EXTRA_STREAM_FORMAT) ?: StreamFormat.DIRECT_MP4.name
        vaultStorageDirPath = intent.getStringExtra(EXTRA_VAULT_DIR)
        isLocalFile = intent.getBooleanExtra(EXTRA_IS_LOCAL_FILE, false)

        val finalUrl = if (isLocalFile) {
            val localFile = File(streamUrl)
            LocalStreamingProxy.instance.getStreamUrlForFile(localFile)
        } else {
            streamUrl
        }
        videoUri = Uri.parse(finalUrl)
    }

    private fun initViews() {
        binding.tvPlayerTitle.text = videoTitle
        binding.tvPlayerSubInfo.text = if (isLocalFile) "Penyimpanan Vault Lokal" else "UC-Engine • Shared Cache Active"

        binding.btnPlayerBack.setOnClickListener {
            finish()
        }

        binding.btnPlayerPlayPause.setOnClickListener {
            togglePlayPause()
        }

        binding.btnPlayerRewind.setOnClickListener {
            seekRelative(-10000)
        }

        binding.btnPlayerForward.setOnClickListener {
            seekRelative(10000)
        }

        binding.btnPlayerSpeed.setOnClickListener {
            cyclePlaybackSpeed()
        }

        binding.btnPlayerPip.setOnClickListener {
            enterPipMode()
        }

        binding.btnPlayerDownload.setOnClickListener {
            triggerIntegratedDownload()
        }

        binding.sbPlayerProgress.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser) {
                    val duration = binding.videoView.duration
                    if (duration > 0) {
                        val seekPos = (progress * duration) / 1000
                        binding.tvPlayerCurrentTime.text = formatTime(seekPos)
                    }
                }
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {
                isUserSeeking = true
                cancelAutoHideControls()
            }

            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                seekBar?.let {
                    val duration = binding.videoView.duration
                    if (duration > 0) {
                        val seekPos = (it.progress * duration) / 1000
                        binding.videoView.seekTo(seekPos)
                    }
                }
                isUserSeeking = false
                scheduleAutoHideControls()
            }
        })
    }

    private fun initPlayback() {
        val uri = videoUri ?: return
        binding.pbBuffering.visibility = View.VISIBLE

        binding.videoView.setVideoURI(uri)
        binding.videoView.setOnPreparedListener { mp ->
            binding.pbBuffering.visibility = View.GONE
            val duration = mp.duration
            binding.tvPlayerTotalTime.text = formatTime(duration)
            binding.videoView.start()
            binding.btnPlayerPlayPause.setImageResource(R.drawable.ic_pause)
            startProgressTracker()
            scheduleAutoHideControls()
        }

        binding.videoView.setOnInfoListener { _, what, _ ->
            when (what) {
                android.media.MediaPlayer.MEDIA_INFO_BUFFERING_START -> {
                    binding.pbBuffering.visibility = View.VISIBLE
                }
                android.media.MediaPlayer.MEDIA_INFO_BUFFERING_END,
                android.media.MediaPlayer.MEDIA_INFO_VIDEO_RENDERING_START -> {
                    binding.pbBuffering.visibility = View.GONE
                }
            }
            true
        }

        binding.videoView.setOnCompletionListener {
            binding.btnPlayerPlayPause.setImageResource(R.drawable.ic_play)
            showControls()
        }

        binding.videoView.setOnErrorListener { _, what, extra ->
            binding.pbBuffering.visibility = View.GONE
            Toast.makeText(this, "Tidak dapat memutar video (Error $what, $extra)", Toast.LENGTH_SHORT).show()
            true
        }
    }

    private fun togglePlayPause() {
        if (binding.videoView.isPlaying) {
            binding.videoView.pause()
            binding.btnPlayerPlayPause.setImageResource(R.drawable.ic_play)
            cancelAutoHideControls()
        } else {
            binding.videoView.start()
            binding.btnPlayerPlayPause.setImageResource(R.drawable.ic_pause)
            scheduleAutoHideControls()
        }
    }

    private fun seekRelative(offsetMs: Int) {
        val current = binding.videoView.currentPosition
        val duration = binding.videoView.duration
        val target = (current + offsetMs).coerceIn(0, duration)
        binding.videoView.seekTo(target)
        scheduleAutoHideControls()
    }

    private fun cyclePlaybackSpeed() {
        currentSpeedIndex = (currentSpeedIndex + 1) % speedOptions.size
        val speed = speedOptions[currentSpeedIndex]
        binding.btnPlayerSpeed.text = "${speed}x"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                val field = binding.videoView.javaClass.getDeclaredField("mMediaPlayer")
                field.isAccessible = true
                val mp = field.get(binding.videoView) as? android.media.MediaPlayer
                mp?.let {
                    val currentParams = it.playbackParams
                    it.playbackParams = currentParams.setSpeed(speed)
                }
            } catch (_: Exception) {}
        }
        scheduleAutoHideControls()
    }

    private fun triggerIntegratedDownload() {
        if (isLocalFile) {
            Toast.makeText(this, "Video ini sudah tersimpan di vault lokal!", Toast.LENGTH_SHORT).show()
            return
        }

        val vaultDir = vaultStorageDirPath?.let { File(it) }
        if (vaultDir == null) {
            Toast.makeText(this, "Vault aktif tidak terdeteksi", Toast.LENGTH_SHORT).show()
            return
        }

        val downloadsFolder = File(vaultDir, "downloads").apply { mkdirs() }
        val cacheFolder = File(vaultDir, "cache/media").apply { mkdirs() }

        val cleanTitle = videoTitle.replace(Regex("[^a-zA-Z0-9._-]"), "_")
        val outputFile = File(downloadsFolder, if (cleanTitle.endsWith(".mp4")) cleanTitle else "$cleanTitle.mp4")

        val format = try {
            StreamFormat.valueOf(streamFormatStr)
        } catch (_: Exception) {
            StreamFormat.DIRECT_MP4
        }

        val stream = DetectedMediaStream(
            id = streamId.ifEmpty { System.currentTimeMillis().toString() },
            url = streamUrl,
            mimeType = "video/mp4",
            format = format,
            title = videoTitle
        )

        // Start download service with shared cache reuse!
        DownloadService.startDownload(this, stream, outputFile, cacheFolder)

        binding.btnPlayerDownload.isEnabled = false
        binding.btnPlayerDownload.text = "Mengunduh"
        binding.tvPlayerDownloadStatus.visibility = View.VISIBLE
        binding.tvPlayerDownloadStatus.text = "Mengunduh: Menggunakan buffer cache player (Tanpa ulang)!"

        Toast.makeText(this, "Unduhan dimulai menggunakan cache player!", Toast.LENGTH_LONG).show()
    }

    private fun observeActiveDownload() {
        val downloader = DownloadService.activeDownloader ?: return
        lifecycleScope.launch {
            downloader.downloadState.collectLatest { state ->
                when (state) {
                    is DownloadState.Downloading -> {
                        binding.tvPlayerDownloadStatus.visibility = View.VISIBLE
                        val speedMb = String.format("%.1f", state.speedBytesPerSec / (1024.0 * 1024.0))
                        binding.tvPlayerDownloadStatus.text = "Mengunduh di latar belakang: ${state.progressPercent}% ($speedMb MB/s)"
                    }
                    is DownloadState.Completed -> {
                        binding.tvPlayerDownloadStatus.visibility = View.VISIBLE
                        binding.tvPlayerDownloadStatus.text = "Unduhan Selesai • Tersimpan di Enclave Vault"
                        binding.btnPlayerDownload.text = "Tersimpan"
                    }
                    is DownloadState.Failed -> {
                        binding.tvPlayerDownloadStatus.visibility = View.VISIBLE
                        binding.tvPlayerDownloadStatus.text = "Unduhan terhenti: ${state.error}"
                        binding.btnPlayerDownload.isEnabled = true
                        binding.btnPlayerDownload.text = "Unduh"
                    }
                    DownloadState.Idle -> {}
                }
            }
        }
    }

    // =========================================================================
    // GESTURE CONTROLS (VOLUME, BRIGHTNESS, SEEK HUD)
    // =========================================================================
    private fun setupGestureDetector() {
        binding.viewGestureTouch.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    touchStartX = event.x
                    touchStartY = event.y
                    initialVolume = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC)
                    initialBrightness = window.attributes.screenBrightness.let { if (it < 0) 0.5f else it }
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val deltaX = event.x - touchStartX
                    val deltaY = event.y - touchStartY

                    if (abs(deltaY) > abs(deltaX) && abs(deltaY) > 20) {
                        val viewWidth = binding.viewGestureTouch.width
                        val isLeftSide = touchStartX < viewWidth / 2

                        if (isLeftSide) {
                            // Gesture Brightness Control (Left side vertical drag)
                            val percentDelta = -deltaY / binding.viewGestureTouch.height
                            val newBrightness = (initialBrightness + percentDelta).coerceIn(0.01f, 1.0f)
                            val lp = window.attributes
                            lp.screenBrightness = newBrightness
                            window.attributes = lp

                            showGestureHud(
                                R.drawable.ic_brightness_medium,
                                "Kecerahan: ${(newBrightness * 100).toInt()}%"
                            )
                        } else {
                            // Gesture Volume Control (Right side vertical drag)
                            val percentDelta = -deltaY / binding.viewGestureTouch.height
                            val volumeDelta = (percentDelta * maxVolume).toInt()
                            val newVolume = (initialVolume + volumeDelta).coerceIn(0, maxVolume)
                            audioManager.setStreamVolume(AudioManager.STREAM_MUSIC, newVolume, 0)

                            val volPercent = (newVolume * 100) / maxVolume
                            showGestureHud(
                                R.drawable.ic_volume_up,
                                "Volume: $volPercent%"
                            )
                        }
                    }
                    true
                }
                MotionEvent.ACTION_UP -> {
                    val deltaX = abs(event.x - touchStartX)
                    val deltaY = abs(event.y - touchStartY)
                    if (deltaX < 15 && deltaY < 15) {
                        toggleControlsVisibility()
                    }
                    hideGestureHudDelayed()
                    true
                }
                else -> false
            }
        }
    }

    private fun showGestureHud(iconRes: Int, text: String) {
        binding.ivGestureIcon.setImageResource(iconRes)
        binding.tvGestureText.text = text
        binding.layoutGestureFeedback.visibility = View.VISIBLE
    }

    private fun hideGestureHudDelayed() {
        handler.postDelayed({
            binding.layoutGestureFeedback.visibility = View.GONE
        }, 800)
    }

    // =========================================================================
    // CONTROLS VISIBILITY & TIMELINE PROGRESS
    // =========================================================================
    private fun toggleControlsVisibility() {
        if (isControlsVisible) hideControls() else showControls()
    }

    private fun showControls() {
        isControlsVisible = true
        binding.layoutControls.visibility = View.VISIBLE
        scheduleAutoHideControls()
    }

    private fun hideControls() {
        isControlsVisible = false
        binding.layoutControls.visibility = View.GONE
        cancelAutoHideControls()
    }

    private val autoHideRunnable = Runnable { hideControls() }

    private fun scheduleAutoHideControls() {
        cancelAutoHideControls()
        handler.postDelayed(autoHideRunnable, 4000)
    }

    private fun cancelAutoHideControls() {
        handler.removeCallbacks(autoHideRunnable)
    }

    private val progressTrackerRunnable = object : Runnable {
        override fun run() {
            if (!isUserSeeking && binding.videoView.isPlaying) {
                val current = binding.videoView.currentPosition
                val duration = binding.videoView.duration
                if (duration > 0) {
                    binding.sbPlayerProgress.progress = (current * 1000) / duration
                    binding.tvPlayerCurrentTime.text = formatTime(current)
                }
            }
            handler.postDelayed(this, 500)
        }
    }

    private fun startProgressTracker() {
        handler.removeCallbacks(progressTrackerRunnable)
        handler.post(progressTrackerRunnable)
    }

    private fun formatTime(ms: Int): String {
        val totalSeconds = (ms / 1000).coerceAtLeast(0)
        val minutes = totalSeconds / 60
        val seconds = totalSeconds % 60
        return String.format("%02d:%02d", minutes, seconds)
    }

    // =========================================================================
    // PICTURE-IN-PICTURE (PiP)
    // =========================================================================
    private fun enterPipMode() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val aspectRatio = Rational(16, 9)
            val pipParams = PictureInPictureParams.Builder()
                .setAspectRatio(aspectRatio)
                .build()
            enterPictureInPictureMode(pipParams)
        } else {
            Toast.makeText(this, "Picture-in-Picture membutuhkan Android 8.0+", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onPictureInPictureModeChanged(isInPictureInPictureMode: Boolean, newConfig: Configuration) {
        super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)
        if (isInPictureInPictureMode) {
            hideControls()
        } else {
            showControls()
        }
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)
        binding.videoView.stopPlayback()
        super.onDestroy()
    }
}
