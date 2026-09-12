package com.yourbrowser.core.crypto

import java.nio.ByteBuffer
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

class AesGcmCipher {

    companion object {
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
        private const val IV_LENGTH_BYTES = 12
        private const val TAG_LENGTH_BITS = 128
    }

    private val secureRandom = SecureRandom()

    /**
     * Mengenkripsi plaintext menggunakan AES-256-GCM.
     * Output format: [12 bytes IV] + [Ciphertext + 16 bytes GCM Auth Tag]
     */
    fun encrypt(plaintext: ByteArray, keyBytes: ByteArray, associatedData: ByteArray? = null): ByteArray {
        val iv = ByteArray(IV_LENGTH_BYTES)
        secureRandom.nextBytes(iv)

        val secretKey = SecretKeySpec(keyBytes, "AES")
        val parameterSpec = GCMParameterSpec(TAG_LENGTH_BITS, iv)

        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, parameterSpec)

        if (associatedData != null) {
            cipher.updateAAD(associatedData)
        }

        val ciphertext = cipher.doFinal(plaintext)

        val byteBuffer = ByteBuffer.allocate(iv.size + ciphertext.size)
        byteBuffer.put(iv)
        byteBuffer.put(ciphertext)

        return byteBuffer.array()
    }

    /**
     * Mendekripsi ciphertext AES-256-GCM.
     * Mengembalikan plaintext, atau melempar Exception jika kunci salah / ciphertext telah dimanipulasi.
     */
    fun decrypt(encryptedPayload: ByteArray, keyBytes: ByteArray, associatedData: ByteArray? = null): ByteArray {
        require(encryptedPayload.size > IV_LENGTH_BYTES) { "Invalid ciphertext length" }

        val iv = ByteArray(IV_LENGTH_BYTES)
        System.arraycopy(encryptedPayload, 0, iv, 0, IV_LENGTH_BYTES)

        val ciphertextOffset = IV_LENGTH_BYTES
        val ciphertextLength = encryptedPayload.size - IV_LENGTH_BYTES

        val secretKey = SecretKeySpec(keyBytes, "AES")
        val parameterSpec = GCMParameterSpec(TAG_LENGTH_BITS, iv)

        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, parameterSpec)

        if (associatedData != null) {
            cipher.updateAAD(associatedData)
        }

        return cipher.doFinal(encryptedPayload, ciphertextOffset, ciphertextLength)
    }
}
