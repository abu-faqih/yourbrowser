package com.yourbrowser.feature.downloader.cache

import java.io.File
import java.security.MessageDigest

/**
 * Pengelola Media Cache Bersama (Unified Media Cache).
 * Menyediakan sinkronisasi cache antara Video Player dan Downloader:
 * - Segmen yang telah di-buffer/ditonton oleh player disimpan di folder cache.
 * - Saat unduhan dipicu, downloader langsung mengadopsi segmen yang ada tanpa mengunduh ulang.
 */
class MediaCacheManager(private val cacheBaseDir: File) {

    init {
        if (!cacheBaseDir.exists()) {
            cacheBaseDir.mkdirs()
        }
    }

    /**
     * Menghasilkan direktori cache spesifik untuk suatu URL media berdasarkan hash SHA-256.
     */
    fun getCacheDirForStream(streamUrl: String): File {
        val hash = MessageDigest.getInstance("SHA-256")
            .digest(streamUrl.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
            .take(16)
        val dir = File(cacheBaseDir, hash)
        if (!dir.exists()) {
            dir.mkdirs()
        }
        return dir
    }

    /**
     * Memeriksa keberadaan segmen yang telah di-cache.
     */
    fun getCachedSegment(streamUrl: String, segmentIndex: Int): File? {
        val segFile = File(getCacheDirForStream(streamUrl), "seg_$segmentIndex.ts")
        return if (segFile.exists() && segFile.length() > 0) segFile else null
    }

    /**
     * Menyimpan data segmen yang di-fetch player ke dalam cache.
     */
    fun storeSegment(streamUrl: String, segmentIndex: Int, data: ByteArray): File {
        val segFile = File(getCacheDirForStream(streamUrl), "seg_$segmentIndex.ts")
        segFile.writeBytes(data)
        return segFile
    }

    /**
     * Mengambil seluruh segmen yang telah di-cache untuk stream tertentu.
     */
    fun getExistingCachedSegments(streamUrl: String): List<File> {
        val streamCache = getCacheDirForStream(streamUrl)
        return streamCache.listFiles()?.filter {
            it.name.startsWith("seg_") && it.name.endsWith(".ts") && it.length() > 0
        }?.sortedBy { file ->
            file.name.removePrefix("seg_").removeSuffix(".ts").toIntOrNull() ?: 0
        } ?: emptyList()
    }

    /**
     * Mengadopsi segmen yang sudah ada di cache pemutar ke folder tujuan unduhan.
     * Mengembalikan daftar index segmen yang sudah lengkap, sehingga downloader
     * hanya perlu meminta segmen yang belum ada ke server.
     */
    fun adoptCacheForDownload(streamUrl: String, targetDir: File): Set<Int> {
        val streamCache = getCacheDirForStream(streamUrl)
        val completedIndices = mutableSetOf<Int>()

        if (!targetDir.exists()) {
            targetDir.mkdirs()
        }

        streamCache.listFiles()?.forEach { file ->
            if (file.name.startsWith("seg_") && file.name.endsWith(".ts") && file.length() > 0) {
                val index = file.name.removePrefix("seg_").removeSuffix(".ts").toIntOrNull()
                if (index != null) {
                    val destFile = File(targetDir, file.name)
                    if (!destFile.exists() || destFile.length() == 0L) {
                        file.copyTo(destFile, overwrite = true)
                    }
                    completedIndices.add(index)
                }
            }
        }
        return completedIndices
    }

    /**
     * Membersihkan cache untuk URL tertentu (misalnya saat vault ditutup).
     */
    fun clearCacheForStream(streamUrl: String) {
        val streamCache = getCacheDirForStream(streamUrl)
        streamCache.deleteRecursively()
    }

    /**
     * Membersihkan seluruh media cache pada vault aktif.
     */
    fun clearAll() {
        cacheBaseDir.deleteRecursively()
        cacheBaseDir.mkdirs()
    }
}
