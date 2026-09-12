package com.yourbrowser.feature.downloader

import com.yourbrowser.feature.downloader.model.StreamFormat
import com.yourbrowser.feature.downloader.parser.HlsManifestParser
import com.yourbrowser.feature.downloader.sniffer.MediaSniffer
import org.junit.Assert.*
import org.junit.Test

class DownloaderUnitTest {

    @Test
    fun testMediaSnifferDirectAndHlsDetection() {
        val sniffer = MediaSniffer()

        // Test 1: Direct MP4
        val s1 = sniffer.inspectNetworkResponse(
            url = "https://cdn.example.com/videos/movie_sample.mp4?token=abc",
            mimeType = "video/mp4",
            contentLength = 50_000_000
        )
        assertNotNull("Direct MP4 should be detected", s1)
        assertEquals(StreamFormat.DIRECT_MP4, s1?.format)

        // Test 2: HLS Playlist
        val s2 = sniffer.inspectNetworkResponse(
            url = "https://streaming.example.com/live/master.m3u8",
            mimeType = "application/x-mpegURL"
        )
        assertNotNull("HLS stream should be detected", s2)
        assertEquals(StreamFormat.HLS_M3U8, s2?.format)

        // Test 3: Standard Web Page (Should NOT be detected)
        val s3 = sniffer.inspectNetworkResponse(
            url = "https://example.com/index.html",
            mimeType = "text/html"
        )
        assertNull("HTML page should not be detected as media stream", s3)

        // Test 4: DOM Registration
        val s4 = sniffer.registerFromDom("blob:https://youtube.com/abc-123", "Sample Blob")
        assertNotNull("Blob URL from DOM should be detected", s4)
        assertEquals(StreamFormat.BLOB_MSE, s4?.format)
    }

    @Test
    fun testHlsManifestParserMasterAndMedia() {
        val parser = HlsManifestParser()

        val masterContent = """
            #EXTM3U
            #EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=720x480
            low.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=2560000,RESOLUTION=1280x720
            mid.m3u8
            #EXT-X-STREAM-INF:BANDWIDTH=7680000,RESOLUTION=1920x1080
            high.m3u8
        """.trimIndent()

        val masterPlaylist = parser.parse(masterContent, "https://cdn.example.com/hls/master.m3u8")
        assertTrue("Must be identified as master playlist", masterPlaylist.isMaster)
        assertEquals(3, masterPlaylist.variants.size)
        // Check sorting (highest bandwidth first)
        assertEquals(7680000L, masterPlaylist.variants[0].bandwidth)
        assertEquals("https://cdn.example.com/hls/high.m3u8", masterPlaylist.variants[0].url)

        val mediaContent = """
            #EXTM3U
            #EXT-X-TARGETDURATION:10
            #EXTINF:9.009,
            segment_0.ts
            #EXTINF:9.009,
            segment_1.ts
        """.trimIndent()

        val mediaPlaylist = parser.parse(mediaContent, "https://cdn.example.com/hls/high.m3u8")
        assertFalse("Must be identified as media playlist", mediaPlaylist.isMaster)
        assertEquals(2, mediaPlaylist.segmentUrls.size)
        assertEquals("https://cdn.example.com/hls/segment_0.ts", mediaPlaylist.segmentUrls[0])
        assertEquals("https://cdn.example.com/hls/segment_1.ts", mediaPlaylist.segmentUrls[1])
    }

    @Test
    fun testMediaCacheManagerStoreAndAdopt() {
        val tempRoot = java.io.File(System.getProperty("java.io.tmpdir"), "yb_test_cache_${System.currentTimeMillis()}").apply { mkdirs() }
        val targetDownloadDir = java.io.File(tempRoot, "downloads").apply { mkdirs() }

        try {
            val cacheManager = com.yourbrowser.feature.downloader.cache.MediaCacheManager(tempRoot)
            val streamUrl = "https://cdn.example.com/hls/test_stream.m3u8"

            // Simpan segmen 0 dan 1 yang diputar oleh video player
            cacheManager.storeSegment(streamUrl, 0, byteArrayOf(0x47, 0x01, 0x02))
            cacheManager.storeSegment(streamUrl, 1, byteArrayOf(0x47, 0x03, 0x04))

            // Periksa segment exists
            assertNotNull(cacheManager.getCachedSegment(streamUrl, 0))
            assertNotNull(cacheManager.getCachedSegment(streamUrl, 1))
            assertNull(cacheManager.getCachedSegment(streamUrl, 2))

            // Adopsi cache ke folder unduhan
            val adopted = cacheManager.adoptCacheForDownload(streamUrl, targetDownloadDir)
            assertEquals(setOf(0, 1), adopted)

            // Pastikan file segmen ada di folder download tanpa perlu fetch ulang
            assertTrue(java.io.File(targetDownloadDir, "seg_0.ts").exists())
            assertTrue(java.io.File(targetDownloadDir, "seg_1.ts").exists())
        } finally {
            tempRoot.deleteRecursively()
        }
    }

    @Test
    fun testLocalPlaylistGenerator() {
        val tempDir = java.io.File(System.getProperty("java.io.tmpdir"), "yb_test_m3u8_${System.currentTimeMillis()}").apply { mkdirs() }
        try {
            val seg0 = java.io.File(tempDir, "seg_0.ts").apply { writeBytes(byteArrayOf(1, 2, 3)) }
            val seg1 = java.io.File(tempDir, "seg_1.ts").apply { writeBytes(byteArrayOf(4, 5, 6)) }

            // 1. Test live playlist while downloading (ongoing event)
            val liveManifest = com.yourbrowser.feature.downloader.player.LocalPlaylistGenerator.updateLocalManifest(
                targetDir = tempDir,
                downloadedSegments = listOf(seg0, seg1),
                targetDurationSec = 10,
                isCompleted = false
            )
            val liveContent = liveManifest.readText()
            assertTrue("Must contain EVENT playlist type", liveContent.contains("#EXT-X-PLAYLIST-TYPE:EVENT"))
            assertFalse("Must NOT contain ENDLIST while downloading", liveContent.contains("#EXT-X-ENDLIST"))
            assertTrue("Must reference seg_0.ts", liveContent.contains("seg_0.ts"))
            assertTrue("Must reference seg_1.ts", liveContent.contains("seg_1.ts"))

            // 2. Test completed playlist
            val completedManifest = com.yourbrowser.feature.downloader.player.LocalPlaylistGenerator.updateLocalManifest(
                targetDir = tempDir,
                downloadedSegments = listOf(seg0, seg1),
                targetDurationSec = 10,
                isCompleted = true
            )
            val completedContent = completedManifest.readText()
            assertTrue("Must contain ENDLIST upon completion", completedContent.contains("#EXT-X-ENDLIST"))
        } finally {
            tempDir.deleteRecursively()
        }
    }
}
