package com.yourbrowser.feature.downloader.player

import java.io.File

/**
 * Generator Manifest HLS (.m3u8) Dinamis Lokal.
 * Memungkinkan pemutar media memutar video yang sedang diunduh secara instan (Play-While-Downloading).
 * File manifest diperbarui secara berkala layaknya live event streaming setiap kali ada segmen baru.
 */
object LocalPlaylistGenerator {

    /**
     * Memperbarui atau membuat file manifest HLS lokal (playback_stream.m3u8).
     *
     * @param targetDir Direktori tempat segmen .ts disimpan.
     * @param downloadedSegments Daftar file segmen .ts yang telah selesai diunduh.
     * @param targetDurationSec Target durasi maksimum per segmen (default 10 detik).
     * @param isCompleted True jika seluruh segmen sudah lengkap diunduh (menambahkan #EXT-X-ENDLIST).
     * @return File manifest .m3u8 yang dihasilkan.
     */
    fun updateLocalManifest(
        targetDir: File,
        downloadedSegments: List<File>,
        targetDurationSec: Int = 10,
        isCompleted: Boolean = false
    ): File {
        val manifestFile = File(targetDir, "playback_stream.m3u8")
        val sortedSegments = downloadedSegments
            .filter { it.exists() && it.length() > 0 }
            .sortedBy { file ->
                file.name.removePrefix("seg_").removeSuffix(".ts").toIntOrNull() ?: 0
            }

        val builder = StringBuilder()
        builder.appendLine("#EXTM3U")
        builder.appendLine("#EXT-X-VERSION:3")
        builder.appendLine("#EXT-X-TARGETDURATION:$targetDurationSec")
        builder.appendLine("#EXT-X-MEDIA-SEQUENCE:0")

        if (!isCompleted) {
            builder.appendLine("#EXT-X-PLAYLIST-TYPE:EVENT")
        }

        for (seg in sortedSegments) {
            builder.appendLine("#EXTINF:$targetDurationSec.0,")
            builder.appendLine(seg.name)
        }

        if (isCompleted) {
            builder.appendLine("#EXT-X-ENDLIST")
        }

        manifestFile.writeText(builder.toString(), Charsets.UTF_8)
        return manifestFile
    }
}
