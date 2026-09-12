package com.yourbrowser.core.crypto

import java.util.Arrays

object MemoryZeroizer {
    /**
     * Membersihkan byte array di memori dengan menuliskan byte 0x00.
     * Mencegah residu kunci kriptografi di heap RAM.
     */
    fun zeroize(bytes: ByteArray?) {
        if (bytes != null) {
            Arrays.fill(bytes, 0.toByte())
        }
    }

    /**
     * Membersihkan char array (misal masukan password pengguna) di RAM.
     */
    fun zeroize(chars: CharArray?) {
        if (chars != null) {
            Arrays.fill(chars, '\u0000')
        }
    }
}
