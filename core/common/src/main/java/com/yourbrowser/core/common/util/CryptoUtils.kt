package com.yourbrowser.core.common.util

object CryptoUtils {
    @OptIn(ExperimentalStdlibApi::class)
    fun bytesToHex(bytes: ByteArray): String {
        return bytes.toHexString()
    }

    @OptIn(ExperimentalStdlibApi::class)
    fun hexToBytes(hex: String): ByteArray {
        return hex.hexToByteArray()
    }
}
