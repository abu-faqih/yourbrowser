package com.yourbrowser.feature.downloader.sniffer

import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.StreamFormat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.net.URI
import java.util.UUID

class MediaSniffer {

    private val _detectedStreams = MutableStateFlow<List<DetectedMediaStream>>(emptyList())
    val detectedStreams: StateFlow<List<DetectedMediaStream>> = _detectedStreams.asStateFlow()

    fun clearStreams() {
        _detectedStreams.value = emptyList()
    }

    /**
     * Menganalisis URL dan header HTTP respons untuk mendeteksi apakah stream video sedang dimuat.
     */
    fun inspectNetworkResponse(
        url: String,
        mimeType: String?,
        contentLength: Long = 0L,
        requestHeaders: Map<String, String> = emptyMap()
    ): DetectedMediaStream? {
        val format = classifyFormat(url, mimeType)
        if (format == StreamFormat.UNKNOWN) return null

        // Hindari duplikasi stream yang sama persis
        val currentList = _detectedStreams.value
        if (currentList.any { it.url == url }) return null

        val detected = DetectedMediaStream(
            id = UUID.randomUUID().toString(),
            url = url,
            mimeType = mimeType ?: defaultMimeForFormat(format),
            format = format,
            title = extractTitleFromUrl(url),
            sizeBytes = contentLength,
            headers = requestHeaders
        )

        _detectedStreams.value = currentList + detected
        return detected
    }

    /**
     * Menerima deteksi langsung dari DOM JavaScript injection (HTMLMediaElement hook).
     */
    fun registerFromDom(mediaSrc: String, pageTitle: String? = null): DetectedMediaStream? {
        if (mediaSrc.isBlank()) return null
        val format = classifyFormat(mediaSrc, null)

        val currentList = _detectedStreams.value
        if (currentList.any { it.url == mediaSrc }) return null

        val detected = DetectedMediaStream(
            id = UUID.randomUUID().toString(),
            url = mediaSrc,
            mimeType = defaultMimeForFormat(format),
            format = format,
            title = pageTitle ?: extractTitleFromUrl(mediaSrc)
        )

        _detectedStreams.value = currentList + detected
        return detected
    }

    private fun classifyFormat(url: String, mimeType: String?): StreamFormat {
        val cleanUrl = url.lowercase().substringBefore("?")
        val cleanMime = mimeType?.lowercase() ?: ""

        return when {
            cleanUrl.endsWith(".m3u8") ||
                    cleanMime.contains("application/x-mpegurl") ||
                    cleanMime.contains("application/vnd.apple.mpegurl") -> StreamFormat.HLS_M3U8

            cleanUrl.endsWith(".mpd") ||
                    cleanMime.contains("application/dash+xml") -> StreamFormat.DASH_MPD

            cleanUrl.endsWith(".mp4") ||
                    cleanMime.contains("video/mp4") -> StreamFormat.DIRECT_MP4

            cleanUrl.endsWith(".webm") ||
                    cleanMime.contains("video/webm") -> StreamFormat.DIRECT_WEBM

            url.startsWith("blob:") -> StreamFormat.BLOB_MSE

            cleanMime.startsWith("video/") -> StreamFormat.DIRECT_MP4

            else -> StreamFormat.UNKNOWN
        }
    }

    private fun defaultMimeForFormat(format: StreamFormat): String {
        return when (format) {
            StreamFormat.HLS_M3U8 -> "application/vnd.apple.mpegurl"
            StreamFormat.DASH_MPD -> "application/dash+xml"
            StreamFormat.DIRECT_MP4 -> "video/mp4"
            StreamFormat.DIRECT_WEBM -> "video/webm"
            StreamFormat.BLOB_MSE -> "video/mp4"
            StreamFormat.UNKNOWN -> "application/octet-stream"
        }
    }

    private fun extractTitleFromUrl(url: String): String {
        return try {
            val uri = URI(url)
            val path = uri.path ?: ""
            val lastSegment = path.substringAfterLast('/')
            if (lastSegment.isNotBlank() && lastSegment.contains('.')) {
                lastSegment
            } else {
                "Video_${System.currentTimeMillis() % 10000}"
            }
        } catch (_: Exception) {
            "Video_${System.currentTimeMillis() % 10000}"
        }
    }
}
