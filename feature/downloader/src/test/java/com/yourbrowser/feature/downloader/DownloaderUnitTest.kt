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
}
