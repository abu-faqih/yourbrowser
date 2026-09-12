package com.yourbrowser.feature.downloader.cache

import java.io.BufferedOutputStream
import java.io.BufferedReader
import java.io.File
import java.io.FileInputStream
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import java.net.URLDecoder
import java.net.URLEncoder
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Loopback HTTP Streaming Server (127.0.0.1).
 * Melayani berkas lokal, playlist HLS dinamis (.m3u8), dan HTTP Range Request (206 Partial Content)
 * untuk mendukung pemutaran progresif video langsung ke Android MediaPlayer (Play-While-Downloading).
 */
class LocalStreamingProxy private constructor() {

    private var serverSocket: ServerSocket? = null
    private val threadPool = Executors.newCachedThreadPool()
    private val isRunning = AtomicBoolean(false)

    var serverPort: Int = 0
        private set

    companion object {
        val instance: LocalStreamingProxy by lazy { LocalStreamingProxy() }
    }

    /**
     * Memulai server proxy loopback pada port bebas (ephemeral port) di 127.0.0.1.
     */
    @Synchronized
    fun start(): Int {
        if (isRunning.get() && serverSocket != null && !serverSocket!!.isClosed) {
            return serverPort
        }

        try {
            val loopback = InetAddress.getByName("127.0.0.1")
            val socket = ServerSocket(0, 50, loopback)
            serverSocket = socket
            serverPort = socket.localPort
            isRunning.set(true)

            threadPool.execute {
                while (isRunning.get() && !socket.isClosed) {
                    try {
                        val clientSocket = socket.accept()
                        threadPool.execute {
                            handleClient(clientSocket)
                        }
                    } catch (_: Exception) {
                        break
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return serverPort
    }

    /**
     * Menghentikan server proxy dan menutup seluruh koneksi.
     */
    @Synchronized
    fun stop() {
        isRunning.set(false)
        try {
            serverSocket?.close()
        } catch (_: Exception) {}
        serverSocket = null
        serverPort = 0
    }

    /**
     * Menghasilkan URL streaming loopback lokal untuk suatu file media atau manifest m3u8.
     */
    fun getStreamUrlForFile(file: File): String {
        start()
        val encodedPath = URLEncoder.encode(file.absolutePath, "UTF-8")
        return "http://127.0.0.1:$serverPort/file?path=$encodedPath"
    }

    private fun handleClient(client: Socket) {
        try {
            client.soTimeout = 10000
            val reader = BufferedReader(InputStreamReader(client.getInputStream(), Charsets.US_ASCII))
            val rawOutput = client.getOutputStream()
            val out = BufferedOutputStream(rawOutput)

            val requestLine = reader.readLine() ?: return
            val parts = requestLine.split(" ")
            if (parts.size < 2) return

            val method = parts[0].uppercase()
            val uri = parts[1]

            // Baca header HTTP
            var rangeHeader: String? = null
            var line: String? = reader.readLine()
            while (!line.isNullOrBlank()) {
                val lower = line.lowercase()
                if (lower.startsWith("range:")) {
                    rangeHeader = line.substring(6).trim()
                }
                line = reader.readLine()
            }

            if (uri.startsWith("/file")) {
                val query = uri.substringAfter("?", "")
                val pathParam = query.split("&").find { it.startsWith("path=") }?.substringAfter("path=")
                if (pathParam != null) {
                    val decodedPath = URLDecoder.decode(pathParam, "UTF-8")
                    val file = File(decodedPath)
                    if (file.exists() && file.isFile) {
                        serveLocalFile(file, method, rangeHeader, out)
                        return
                    }
                }
            }

            // 404 jika file tidak ditemukan
            send404(out)
        } catch (_: Exception) {
        } finally {
            try { client.close() } catch (_: Exception) {}
        }
    }

    private fun serveLocalFile(file: File, method: String, rangeHeader: String?, out: OutputStream) {
        val fileLength = file.length()
        val mimeType = getMimeType(file.name)

        var startOffset = 0L
        var endOffset = fileLength - 1
        var isPartial = false

        if (!rangeHeader.isNullOrBlank() && rangeHeader.startsWith("bytes=")) {
            val rangeSpec = rangeHeader.substring(6).trim()
            val rangeParts = rangeSpec.split("-")
            try {
                if (rangeParts[0].isNotEmpty()) {
                    startOffset = rangeParts[0].toLong()
                }
                if (rangeParts.size > 1 && rangeParts[1].isNotEmpty()) {
                    endOffset = rangeParts[1].toLong()
                }
                if (endOffset >= fileLength) {
                    endOffset = fileLength - 1
                }
                if (startOffset <= endOffset) {
                    isPartial = true
                }
            } catch (_: Exception) {}
        }

        val contentLen = if (fileLength > 0) (endOffset - startOffset + 1).coerceAtLeast(0L) else 0L

        val headerBuilder = StringBuilder()
        if (isPartial) {
            headerBuilder.append("HTTP/1.1 206 Partial Content\r\n")
            headerBuilder.append("Content-Range: bytes $startOffset-$endOffset/$fileLength\r\n")
        } else {
            headerBuilder.append("HTTP/1.1 200 OK\r\n")
        }

        headerBuilder.append("Content-Type: $mimeType\r\n")
        headerBuilder.append("Content-Length: $contentLen\r\n")
        headerBuilder.append("Accept-Ranges: bytes\r\n")
        headerBuilder.append("Access-Control-Allow-Origin: *\r\n")
        headerBuilder.append("Cache-Control: no-cache, no-store\r\n")
        headerBuilder.append("Connection: close\r\n\r\n")

        out.write(headerBuilder.toString().toByteArray(Charsets.US_ASCII))
        out.flush()

        if (method == "HEAD") {
            return
        }

        if (contentLen > 0) {
            FileInputStream(file).use { input ->
                if (startOffset > 0) {
                    input.skip(startOffset)
                }
                val buffer = ByteArray(32768)
                var bytesRemaining = contentLen
                while (bytesRemaining > 0) {
                    val readLen = input.read(buffer, 0, minOf(buffer.size.toLong(), bytesRemaining).toInt())
                    if (readLen < 0) break
                    out.write(buffer, 0, readLen)
                    bytesRemaining -= readLen
                }
                out.flush()
            }
        }
    }

    private fun send404(out: OutputStream) {
        val res = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
        out.write(res.toByteArray(Charsets.US_ASCII))
        out.flush()
    }

    private fun getMimeType(fileName: String): String {
        val lower = fileName.lowercase()
        return when {
            lower.endsWith(".m3u8") -> "application/vnd.apple.mpegurl"
            lower.endsWith(".ts") -> "video/MP2T"
            lower.endsWith(".mp4") -> "video/mp4"
            lower.endsWith(".webm") -> "video/webm"
            lower.endsWith(".mpd") -> "application/dash+xml"
            else -> "application/octet-stream"
        }
    }
}
