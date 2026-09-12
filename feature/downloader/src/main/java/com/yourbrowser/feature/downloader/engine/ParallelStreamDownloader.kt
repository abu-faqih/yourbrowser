package com.yourbrowser.feature.downloader.engine

import com.yourbrowser.core.network.NetworkClientProvider
import com.yourbrowser.feature.downloader.cache.LocalStreamingProxy
import com.yourbrowser.feature.downloader.cache.MediaCacheManager
import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.DownloadState
import com.yourbrowser.feature.downloader.model.StreamFormat
import com.yourbrowser.feature.downloader.parser.HlsManifestParser
import com.yourbrowser.feature.downloader.player.LocalPlaylistGenerator
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.atomic.AtomicLong

class ParallelStreamDownloader(
    private val client: OkHttpClient = NetworkClientProvider.client,
    private val hlsParser: HlsManifestParser = HlsManifestParser(),
    private val maxConcurrentChunks: Int = 4,
    var cacheManager: MediaCacheManager? = null
) {

    private val _downloadState = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadState: StateFlow<DownloadState> = _downloadState.asStateFlow()

    @Volatile
    private var isCancelled = false

    @Volatile
    var activeProgressiveUrl: String? = null
        private set

    fun cancel() {
        isCancelled = true
    }

    /**
     * Memulai proses pengunduhan media stream ke file tujuan dengan dukungan
     * Unified Cache reuse dan Progressive Playback (Play-While-Downloading).
     */
    suspend fun download(stream: DetectedMediaStream, destinationFile: File): Unit = withContext(Dispatchers.IO) {
        isCancelled = false
        activeProgressiveUrl = null
        _downloadState.value = DownloadState.Downloading(
            streamId = stream.id,
            downloadedBytes = 0,
            totalBytes = stream.sizeBytes,
            progressPercent = 0,
            speedBytesPerSec = 0
        )

        try {
            when (stream.format) {
                StreamFormat.DIRECT_MP4,
                StreamFormat.DIRECT_WEBM,
                StreamFormat.UNKNOWN -> {
                    downloadDirectStream(stream, destinationFile)
                }

                StreamFormat.HLS_M3U8 -> {
                    downloadHlsStream(stream, destinationFile)
                }

                StreamFormat.DASH_MPD,
                StreamFormat.BLOB_MSE -> {
                    downloadDirectStream(stream, destinationFile)
                }
            }

            if (!isCancelled) {
                _downloadState.value = DownloadState.Completed(
                    streamId = stream.id,
                    localFilePath = destinationFile.absolutePath
                )
            }
        } catch (e: Exception) {
            if (e is CancellationException || isCancelled) {
                _downloadState.value = DownloadState.Failed(stream.id, "Download dibatalkan oleh pengguna")
            } else {
                _downloadState.value = DownloadState.Failed(stream.id, e.message ?: "Unknown download error")
            }
            destinationFile.delete()
        }
        Unit
    }

    private suspend fun downloadDirectStream(stream: DetectedMediaStream, destinationFile: File) {
        val requestBuilder = Request.Builder().url(stream.url)
        stream.headers.forEach { (k, v) -> requestBuilder.addHeader(k, v) }

        client.newCall(requestBuilder.build()).execute().use { response ->
            if (!response.isSuccessful) throw IllegalStateException("HTTP ${response.code}: ${response.message}")
            val body = response.body ?: throw IllegalStateException("Empty response body")
            val contentLength = body.contentLength()

            val progressiveUrl = LocalStreamingProxy.instance.getStreamUrlForFile(destinationFile)
            activeProgressiveUrl = progressiveUrl

            val buffer = ByteArray(16384)
            var bytesCopied = 0L
            val startTime = System.currentTimeMillis()

            body.byteStream().use { input ->
                FileOutputStream(destinationFile).use { output ->
                    while (true) {
                        if (isCancelled) throw CancellationException("Download cancelled")
                        val bytes = input.read(buffer)
                        if (bytes < 0) break
                        output.write(buffer, 0, bytes)
                        output.flush()
                        bytesCopied += bytes

                        val elapsedSec = (System.currentTimeMillis() - startTime).coerceAtLeast(1) / 1000.0
                        val speed = (bytesCopied / elapsedSec).toLong()
                        val progressPercent = if (contentLength > 0) ((bytesCopied * 100) / contentLength).toInt() else 0

                        _downloadState.value = DownloadState.Downloading(
                            streamId = stream.id,
                            downloadedBytes = bytesCopied,
                            totalBytes = contentLength,
                            progressPercent = progressPercent,
                            speedBytesPerSec = speed,
                            progressivePlaybackUrl = progressiveUrl
                        )
                    }
                }
            }
        }
    }

    private suspend fun downloadHlsStream(stream: DetectedMediaStream, destinationFile: File) {
        // 1. Fetch manifest m3u8
        val manifestContent = fetchString(stream.url, stream.headers)
        val playlist = hlsParser.parse(manifestContent, stream.url)

        val targetSegments = if (playlist.isMaster && playlist.variants.isNotEmpty()) {
            val bestVariant = playlist.variants.first()
            val mediaPlaylistContent = fetchString(bestVariant.url, stream.headers)
            hlsParser.parse(mediaPlaylistContent, bestVariant.url).segmentUrls
        } else {
            playlist.segmentUrls
        }

        if (targetSegments.isEmpty()) {
            throw IllegalStateException("Tidak ada segmen media ditemukan pada manifest HLS")
        }

        val totalSegments = targetSegments.size
        val downloadedBytesCount = AtomicLong(0L)
        val completedSegmentsCount = AtomicLong(0L)
        val startTime = System.currentTimeMillis()

        val tempDir = File(destinationFile.parentFile, "temp_${System.currentTimeMillis()}").apply { mkdirs() }
        val segmentFiles = Array<File?>(totalSegments) { null }

        // ADOPT CACHED SEGMENTS FROM PLAYER BUFFER (Zero-Waste Caching)
        val adoptedIndices = cacheManager?.adoptCacheForDownload(stream.url, tempDir) ?: emptySet()
        for (idx in adoptedIndices) {
            if (idx in 0 until totalSegments) {
                val adoptedFile = File(tempDir, "seg_$idx.ts")
                if (adoptedFile.exists() && adoptedFile.length() > 0) {
                    segmentFiles[idx] = adoptedFile
                    downloadedBytesCount.addAndGet(adoptedFile.length())
                    completedSegmentsCount.incrementAndGet()
                }
            }
        }

        // Buat manifest awal jika sudah ada segmen dari cache
        if (completedSegmentsCount.get() > 0) {
            val liveManifest = LocalPlaylistGenerator.updateLocalManifest(
                tempDir,
                segmentFiles.filterNotNull(),
                isCompleted = false
            )
            val progressiveUrl = LocalStreamingProxy.instance.getStreamUrlForFile(liveManifest)
            activeProgressiveUrl = progressiveUrl
            val initProgress = ((completedSegmentsCount.get() * 100) / totalSegments).toInt()
            _downloadState.value = DownloadState.Downloading(
                streamId = stream.id,
                downloadedBytes = downloadedBytesCount.get(),
                totalBytes = 0L,
                progressPercent = initProgress,
                speedBytesPerSec = 0L,
                progressivePlaybackUrl = progressiveUrl
            )
        }

        val semaphore = Semaphore(maxConcurrentChunks)

        try {
            coroutineScope {
                val jobs = targetSegments.mapIndexed { index, segmentUrl ->
                    async(Dispatchers.IO) {
                        // Lewati jika segmen sudah di-cache saat ditonton sebelumnya
                        if (segmentFiles[index] != null && segmentFiles[index]!!.exists() && segmentFiles[index]!!.length() > 0) {
                            return@async
                        }

                        semaphore.withPermit {
                            if (isCancelled) throw CancellationException("Download cancelled")
                            val segFile = File(tempDir, "seg_$index.ts")
                            downloadChunkToFile(segmentUrl, stream.headers, segFile)
                            val size = segFile.length()
                            val curBytes = downloadedBytesCount.addAndGet(size)
                            val doneCount = completedSegmentsCount.incrementAndGet()
                            segmentFiles[index] = segFile

                            // Simpan juga ke cache manager agar player bisa memanfaatkannya
                            cacheManager?.storeSegment(stream.url, index, segFile.readBytes())

                            // Update live playlist untuk play-while-downloading
                            val liveManifest = LocalPlaylistGenerator.updateLocalManifest(
                                tempDir,
                                segmentFiles.filterNotNull(),
                                isCompleted = false
                            )
                            val progressiveUrl = LocalStreamingProxy.instance.getStreamUrlForFile(liveManifest)
                            activeProgressiveUrl = progressiveUrl

                            val elapsedSec = (System.currentTimeMillis() - startTime).coerceAtLeast(1) / 1000.0
                            val speed = (curBytes / elapsedSec).toLong()
                            val progressPercent = ((doneCount * 100) / totalSegments).toInt()

                            _downloadState.value = DownloadState.Downloading(
                                streamId = stream.id,
                                downloadedBytes = curBytes,
                                totalBytes = 0L,
                                progressPercent = progressPercent,
                                speedBytesPerSec = speed,
                                progressivePlaybackUrl = progressiveUrl
                            )
                        }
                    }
                }
                jobs.awaitAll()
            }

            // Tandai manifest lokal sebagai selesai
            LocalPlaylistGenerator.updateLocalManifest(
                tempDir,
                segmentFiles.filterNotNull(),
                isCompleted = true
            )

            // Gabungkan seluruh segmen TS menjadi satu file destinationFile
            FileOutputStream(destinationFile).use { output ->
                for (seg in segmentFiles) {
                    if (seg != null && seg.exists()) {
                        seg.inputStream().use { it.copyTo(output) }
                    }
                }
            }
        } finally {
            tempDir.deleteRecursively()
        }
    }

    private fun fetchString(url: String, headers: Map<String, String>): String {
        val req = Request.Builder().url(url)
        headers.forEach { (k, v) -> req.addHeader(k, v) }
        client.newCall(req.build()).execute().use { resp ->
            if (!resp.isSuccessful) throw IllegalStateException("HTTP ${resp.code} saat fetch manifest")
            return resp.body?.string() ?: ""
        }
    }

    private fun downloadChunkToFile(url: String, headers: Map<String, String>, targetFile: File) {
        val req = Request.Builder().url(url)
        headers.forEach { (k, v) -> req.addHeader(k, v) }
        client.newCall(req.build()).execute().use { resp ->
            if (!resp.isSuccessful) throw IllegalStateException("HTTP ${resp.code} saat download segmen: $url")
            val body = resp.body ?: return
            FileOutputStream(targetFile).use { output ->
                body.byteStream().copyTo(output)
            }
        }
    }
}
