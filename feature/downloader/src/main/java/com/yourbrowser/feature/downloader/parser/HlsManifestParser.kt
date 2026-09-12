package com.yourbrowser.feature.downloader.parser

import java.net.URI

data class HlsVariant(
    val bandwidth: Long,
    val resolution: String?,
    val url: String
)

data class HlsPlaylist(
    val isMaster: Boolean,
    val variants: List<HlsVariant> = emptyList(),
    val segmentUrls: List<String> = emptyList(),
    val targetDurationSeconds: Double = 0.0
)

class HlsManifestParser {

    /**
     * Mem-parsing string konten manifest m3u8 dan menghasilkan HlsPlaylist.
     * Secara otomatis menyelesaikan relative URI terhadap baseUrl.
     */
    fun parse(manifestContent: String, baseUrl: String): HlsPlaylist {
        val lines = manifestContent.lines().map { it.trim() }.filter { it.isNotEmpty() }

        val isMaster = lines.any { it.startsWith("#EXT-X-STREAM-INF") }

        return if (isMaster) {
            parseMasterPlaylist(lines, baseUrl)
        } else {
            parseMediaPlaylist(lines, baseUrl)
        }
    }

    private fun parseMasterPlaylist(lines: List<String>, baseUrl: String): HlsPlaylist {
        val variants = mutableListOf<HlsVariant>()
        var currentBandwidth: Long = 0
        var currentResolution: String? = null

        for (line in lines) {
            if (line.startsWith("#EXT-X-STREAM-INF:")) {
                currentBandwidth = extractAttributeLong(line, "BANDWIDTH") ?: 0L
                currentResolution = extractAttributeString(line, "RESOLUTION")
            } else if (!line.startsWith("#") && currentBandwidth > 0) {
                val resolvedUrl = resolveUrl(baseUrl, line)
                variants.add(HlsVariant(currentBandwidth, currentResolution, resolvedUrl))
                currentBandwidth = 0
                currentResolution = null
            }
        }

        // Urutkan dari resolusi / bandwidth tertinggi
        variants.sortByDescending { it.bandwidth }
        return HlsPlaylist(isMaster = true, variants = variants)
    }

    private fun parseMediaPlaylist(lines: List<String>, baseUrl: String): HlsPlaylist {
        val segments = mutableListOf<String>()
        var targetDuration = 0.0

        for (line in lines) {
            if (line.startsWith("#EXT-X-TARGETDURATION:")) {
                targetDuration = line.substringAfter(":").trim().toDoubleOrNull() ?: 0.0
            } else if (!line.startsWith("#")) {
                segments.add(resolveUrl(baseUrl, line))
            }
        }

        return HlsPlaylist(
            isMaster = false,
            segmentUrls = segments,
            targetDurationSeconds = targetDuration
        )
    }

    private fun resolveUrl(baseUrl: String, relativeOrAbsolute: String): String {
        return try {
            val baseUri = URI(baseUrl)
            baseUri.resolve(relativeOrAbsolute).toString()
        } catch (_: Exception) {
            if (relativeOrAbsolute.startsWith("http://") || relativeOrAbsolute.startsWith("https://")) {
                relativeOrAbsolute
            } else {
                val cleanBase = baseUrl.substringBeforeLast("/")
                "$cleanBase/$relativeOrAbsolute"
            }
        }
    }

    private fun extractAttributeLong(line: String, attrName: String): Long? {
        val regex = Regex("""$attrName=(\d+)""")
        return regex.find(line)?.groupValues?.get(1)?.toLongOrNull()
    }

    private fun extractAttributeString(line: String, attrName: String): String? {
        val regex = Regex("""$attrName=([^,]+)""")
        return regex.find(line)?.groupValues?.get(1)?.replace("\"", "")
    }
}
