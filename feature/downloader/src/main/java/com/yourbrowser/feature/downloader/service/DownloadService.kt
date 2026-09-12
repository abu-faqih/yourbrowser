package com.yourbrowser.feature.downloader.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.yourbrowser.feature.downloader.cache.MediaCacheManager
import com.yourbrowser.feature.downloader.engine.ParallelStreamDownloader
import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.DownloadState
import com.yourbrowser.feature.downloader.model.StreamFormat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.io.File

class DownloadService : Service() {

    private val serviceScope = CoroutineScope(Dispatchers.Main + Job())
    private lateinit var downloader: ParallelStreamDownloader
    private lateinit var notificationManager: NotificationManager

    companion object {
        const val CHANNEL_ID = "yourbrowser_downloads"
        const val NOTIFICATION_ID = 1001

        const val ACTION_START_DOWNLOAD = "com.yourbrowser.action.START_DOWNLOAD"
        const val ACTION_CANCEL_DOWNLOAD = "com.yourbrowser.action.CANCEL_DOWNLOAD"

        const val EXTRA_STREAM_ID = "extra_stream_id"
        const val EXTRA_STREAM_URL = "extra_stream_url"
        const val EXTRA_STREAM_MIME = "extra_stream_mime"
        const val EXTRA_STREAM_FORMAT = "extra_stream_format"
        const val EXTRA_STREAM_TITLE = "extra_stream_title"
        const val EXTRA_DEST_PATH = "extra_dest_path"
        const val EXTRA_CACHE_DIR = "extra_cache_dir"

        var activeDownloader: ParallelStreamDownloader? = null
            internal set
        var activeStream: DetectedMediaStream? = null
            internal set
        var activeDestFile: File? = null
            internal set

        fun startDownload(
            context: Context,
            stream: DetectedMediaStream,
            destFile: File,
            cacheDir: File? = null
        ) {
            val intent = Intent(context, DownloadService::class.java).apply {
                action = ACTION_START_DOWNLOAD
                putExtra(EXTRA_STREAM_ID, stream.id)
                putExtra(EXTRA_STREAM_URL, stream.url)
                putExtra(EXTRA_STREAM_MIME, stream.mimeType)
                putExtra(EXTRA_STREAM_FORMAT, stream.format.name)
                putExtra(EXTRA_STREAM_TITLE, stream.title)
                putExtra(EXTRA_DEST_PATH, destFile.absolutePath)
                if (cacheDir != null) {
                    putExtra(EXTRA_CACHE_DIR, cacheDir.absolutePath)
                }
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun cancelDownload(context: Context) {
            val intent = Intent(context, DownloadService::class.java).apply {
                action = ACTION_CANCEL_DOWNLOAD
            }
            context.startService(intent)
        }
    }

    override fun onCreate() {
        super.onCreate()
        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        downloader = ParallelStreamDownloader()
        activeDownloader = downloader
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_DOWNLOAD -> {
                val streamId = intent.getStringExtra(EXTRA_STREAM_ID) ?: return START_NOT_STICKY
                val streamUrl = intent.getStringExtra(EXTRA_STREAM_URL) ?: return START_NOT_STICKY
                val mimeType = intent.getStringExtra(EXTRA_STREAM_MIME) ?: "video/mp4"
                val formatStr = intent.getStringExtra(EXTRA_STREAM_FORMAT) ?: StreamFormat.DIRECT_MP4.name
                val title = intent.getStringExtra(EXTRA_STREAM_TITLE) ?: "Video Stream"
                val destPath = intent.getStringExtra(EXTRA_DEST_PATH) ?: return START_NOT_STICKY
                val cacheDirPath = intent.getStringExtra(EXTRA_CACHE_DIR)

                val destFile = File(destPath)
                if (cacheDirPath != null) {
                    downloader.cacheManager = MediaCacheManager(File(cacheDirPath))
                }

                val stream = DetectedMediaStream(
                    id = streamId,
                    url = streamUrl,
                    mimeType = mimeType,
                    format = try { StreamFormat.valueOf(formatStr) } catch (_: Exception) { StreamFormat.DIRECT_MP4 },
                    title = title
                )

                activeStream = stream
                activeDestFile = destFile

                startForeground(NOTIFICATION_ID, buildProgressNotification(title, 0, 0))

                serviceScope.launch {
                    launch {
                        downloader.downloadState.collectLatest { state ->
                            when (state) {
                                is DownloadState.Downloading -> {
                                    val notif = buildProgressNotification(
                                        title,
                                        state.progressPercent,
                                        state.speedBytesPerSec
                                    )
                                    notificationManager.notify(NOTIFICATION_ID, notif)
                                }
                                is DownloadState.Completed -> {
                                    val completedNotif = NotificationCompat.Builder(this@DownloadService, CHANNEL_ID)
                                        .setContentTitle("Unduhan Selesai")
                                        .setContentText(title)
                                        .setSmallIcon(android.R.drawable.stat_sys_download_done)
                                        .setAutoCancel(true)
                                        .build()
                                    notificationManager.notify(NOTIFICATION_ID + 1, completedNotif)
                                    stopForeground(STOP_FOREGROUND_REMOVE)
                                    stopSelf()
                                }
                                is DownloadState.Failed -> {
                                    val failedNotif = NotificationCompat.Builder(this@DownloadService, CHANNEL_ID)
                                        .setContentTitle("Unduhan Gagal")
                                        .setContentText(state.error)
                                        .setSmallIcon(android.R.drawable.stat_notify_error)
                                        .setAutoCancel(true)
                                        .build()
                                    notificationManager.notify(NOTIFICATION_ID + 2, failedNotif)
                                    stopForeground(STOP_FOREGROUND_REMOVE)
                                    stopSelf()
                                }
                                DownloadState.Idle -> {}
                            }
                        }
                    }

                    downloader.download(stream, destFile)
                }
            }

            ACTION_CANCEL_DOWNLOAD -> {
                downloader.cancel()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        serviceScope.cancel()
        activeDownloader = null
        activeStream = null
        activeDestFile = null
        super.onDestroy()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Unduhan Video YourBrowser",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Menampilkan progres unduhan video streaming"
            }
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun buildProgressNotification(title: String, percent: Int, speedBps: Long): Notification {
        val speedKb = speedBps / 1024
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Mengunduh Video")
            .setContentText("$title ($percent% - ${speedKb} KB/s)")
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setProgress(100, percent, percent <= 0)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .build()
    }
}
