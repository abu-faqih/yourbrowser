package com.yourbrowser.feature.downloader.model

enum class StreamFormat {
    DIRECT_MP4,
    DIRECT_WEBM,
    HLS_M3U8,
    DASH_MPD,
    BLOB_MSE,
    UNKNOWN
}

data class DetectedMediaStream(
    val id: String,
    val url: String,
    val mimeType: String,
    val format: StreamFormat,
    val title: String = "Media Stream",
    val resolution: String? = null,
    val sizeBytes: Long = 0L,
    val headers: Map<String, String> = emptyMap(),
    val detectedAtEpoch: Long = System.currentTimeMillis()
)

sealed class DownloadState {
    data object Idle : DownloadState()
    data class Downloading(
        val streamId: String,
        val downloadedBytes: Long,
        val totalBytes: Long,
        val progressPercent: Int,
        val speedBytesPerSec: Long,
        val progressivePlaybackUrl: String? = null
    ) : DownloadState()
    data class Completed(val streamId: String, val localFilePath: String) : DownloadState()
    data class Failed(val streamId: String, val error: String) : DownloadState()
}
