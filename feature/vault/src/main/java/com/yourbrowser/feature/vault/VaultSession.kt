package com.yourbrowser.feature.vault

import java.io.File

data class VaultSession(
    val vaultId: String,
    val storageDir: File,
    val masterKey: ByteArray,
    val isDecoy: Boolean = false,
    val createdAtEpoch: Long = System.currentTimeMillis()
) {
    fun wipe() {
        com.yourbrowser.core.crypto.MemoryZeroizer.zeroize(masterKey)
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as VaultSession
        return vaultId == other.vaultId && storageDir == other.storageDir
    }

    override fun hashCode(): Int {
        var result = vaultId.hashCode()
        result = 31 * result + storageDir.hashCode()
        return result
    }
}
