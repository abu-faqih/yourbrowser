package com.yourbrowser.core.crypto

import com.yourbrowser.core.common.util.CryptoUtils
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

data class VaultCredentials(
    val vaultId: String,
    val masterKey: ByteArray
) {
    fun wipe() {
        MemoryZeroizer.zeroize(masterKey)
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as VaultCredentials
        return vaultId == other.vaultId && masterKey.contentEquals(other.masterKey)
    }

    override fun hashCode(): Int {
        var result = vaultId.hashCode()
        result = 31 * result + masterKey.contentHashCode()
        return result
    }
}

class KeyDerivationEngine(
    private val iterations: Int = 65_536,
    private val keyLengthBits: Int = 256
) {
    // Pepper statis aplikasi untuk menambah entropi domain
    private val appPepper = "YourBrowser_ZeroKnowledge_Vault_v1".toByteArray(Charsets.UTF_8)

    /**
     * Menghasilkan kredensial vault secara deterministik dari password pengguna.
     * Tidak ada master database akun: Password yang berbeda menghasilkan VaultId dan Kunci yang unik.
     */
    fun deriveCredentials(passwordChars: CharArray, customSalt: ByteArray? = null): VaultCredentials {
        val salt = customSalt ?: computeDeterministicSalt(passwordChars)
        val spec = PBEKeySpec(passwordChars, salt, iterations, keyLengthBits)
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val derivedBytes = factory.generateSecret(spec).encoded

        // VaultId dihitung dari SHA-256 (derivedKey + appPepper)
        val digest = MessageDigest.getInstance("SHA-256")
        digest.update(derivedBytes)
        digest.update(appPepper)
        val vaultIdHex = CryptoUtils.bytesToHex(digest.digest())

        return VaultCredentials(
            vaultId = vaultIdHex,
            masterKey = derivedBytes
        )
    }

    private fun computeDeterministicSalt(passwordChars: CharArray): ByteArray {
        val digest = MessageDigest.getInstance("SHA-256")
        digest.update(appPepper)
        val pwdBytes = Charsets.UTF_8.encode(java.nio.CharBuffer.wrap(passwordChars)).array()
        val salt = digest.digest(pwdBytes)
        MemoryZeroizer.zeroize(pwdBytes)
        return salt
    }

    companion object {
        fun generateRandomSalt(length: Int = 16): ByteArray {
            val salt = ByteArray(length)
            SecureRandom().nextBytes(salt)
            return salt
        }
    }
}
