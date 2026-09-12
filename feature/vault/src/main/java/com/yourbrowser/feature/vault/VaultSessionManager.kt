package com.yourbrowser.feature.vault

import android.content.Context
import com.yourbrowser.core.crypto.AesGcmCipher
import com.yourbrowser.core.crypto.KeyDerivationEngine
import com.yourbrowser.core.crypto.MemoryZeroizer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File

class VaultSessionManager(
    private val context: Context,
    private val kdfEngine: KeyDerivationEngine = KeyDerivationEngine(),
    private val cipher: AesGcmCipher = AesGcmCipher()
) {
    private val _activeSession = MutableStateFlow<VaultSession?>(null)
    val activeSession: StateFlow<VaultSession?> = _activeSession.asStateFlow()

    private val vaultsBaseDir: File
        get() = File(context.filesDir, "vaults").apply {
            if (!exists()) mkdirs()
        }

    /**
     * Membuka atau membuat partisi vault berdasarkan password.
     * Sifat Zero-Knowledge: password berbeda otomatis membuka direktori terisolasi yang berbeda.
     */
    @Synchronized
    fun unlockVault(passwordChars: CharArray): VaultSession {
        // Jika ada sesi aktif sebelumnya, tutup dan wipe terlebih dahulu
        lockActiveVault()

        val credentials = kdfEngine.deriveCredentials(passwordChars)
        // Segera bersihkan password masukan pengguna dari RAM
        MemoryZeroizer.zeroize(passwordChars)

        val vaultDir = File(vaultsBaseDir, credentials.vaultId).apply {
            if (!exists()) mkdirs()
        }

        // Siapkan subfolder terisolasi untuk data browser: cookies, cache, webstorage
        File(vaultDir, "browser_profile").mkdirs()
        File(vaultDir, "downloads").mkdirs()

        val session = VaultSession(
            vaultId = credentials.vaultId,
            storageDir = vaultDir,
            masterKey = credentials.masterKey
        )

        _activeSession.value = session
        return session
    }

    /**
     * Mengunci sesi aktif: Menghapus pointer sesi dan melakukan zero-out master encryption key di RAM.
     */
    @Synchronized
    fun lockActiveVault() {
        val current = _activeSession.value
        if (current != null) {
            current.wipe()
            _activeSession.value = null
        }
    }

    /**
     * Panic Wipe: Mengunci sesi dan menghapus direktori temporary cache.
     */
    @Synchronized
    fun panicWipe() {
        lockActiveVault()
        // Bersihkan temporary files di cache directory
        context.cacheDir.deleteRecursively()
    }

    /**
     * Menyimpan data rahasia (bookmark/history/notes) ke dalam file terenkripsi AES-256-GCM di vault terkait.
     */
    fun writeEncryptedFile(fileName: String, data: ByteArray) {
        val session = _activeSession.value ?: throw IllegalStateException("No active vault mounted")
        val targetFile = File(session.storageDir, fileName)
        val encrypted = cipher.encrypt(data, session.masterKey)
        targetFile.writeBytes(encrypted)
    }

    /**
     * Membaca dan mendekripsi data dari file terenkripsi di vault terkait.
     */
    fun readEncryptedFile(fileName: String): ByteArray? {
        val session = _activeSession.value ?: throw IllegalStateException("No active vault mounted")
        val targetFile = File(session.storageDir, fileName)
        if (!targetFile.exists()) return null
        val encrypted = targetFile.readBytes()
        return cipher.decrypt(encrypted, session.masterKey)
    }
}
