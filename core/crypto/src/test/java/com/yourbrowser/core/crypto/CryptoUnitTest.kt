package com.yourbrowser.core.crypto

import org.junit.Assert.*
import org.junit.Test

class CryptoUnitTest {

    private val kdfEngine = KeyDerivationEngine(iterations = 1000) // Lower iteration for fast unit test
    private val cipher = AesGcmCipher()

    @Test
    fun testKeyDerivationDeterminismAndDifferentPasswords() {
        val passA = "PasswordA_Secret123".toCharArray()
        val credsA1 = kdfEngine.deriveCredentials(passA)
        val credsA2 = kdfEngine.deriveCredentials(passA)

        // Password yang sama harus menghasilkan VaultId yang sama
        assertEquals("Deterministic VaultId check", credsA1.vaultId, credsA2.vaultId)
        assertArrayEquals("Deterministic Key check", credsA1.masterKey, credsA2.masterKey)

        // Password yang berbeda harus menghasilkan VaultId yang berbeda
        val passB = "PasswordB_Different456".toCharArray()
        val credsB = kdfEngine.deriveCredentials(passB)

        assertNotEquals("Different password must produce different VaultId", credsA1.vaultId, credsB.vaultId)
        assertFalse("Different password must produce different Key", credsA1.masterKey.contentEquals(credsB.masterKey))
    }

    @Test
    fun testAesGcmEncryptAndDecrypt() {
        val password = "StrongPassword789".toCharArray()
        val creds = kdfEngine.deriveCredentials(password)

        val plaintext = "Secret Session Cookie & History Data".toByteArray(Charsets.UTF_8)
        val ciphertext = cipher.encrypt(plaintext, creds.masterKey)

        assertFalse("Ciphertext should not equal plaintext", ciphertext.contentEquals(plaintext))

        val decrypted = cipher.decrypt(ciphertext, creds.masterKey)
        val decryptedText = String(decrypted, Charsets.UTF_8)

        assertEquals("Decrypted text must match original plaintext", "Secret Session Cookie & History Data", decryptedText)
    }

    @Test
    fun testAesGcmTamperResistance() {
        val password = "StrongPassword789".toCharArray()
        val creds = kdfEngine.deriveCredentials(password)

        val plaintext = "Integrity Protected Data".toByteArray(Charsets.UTF_8)
        val ciphertext = cipher.encrypt(plaintext, creds.masterKey)

        // Modifikasi 1 byte di tengah ciphertext
        ciphertext[ciphertext.size - 5] = (ciphertext[ciphertext.size - 5] + 1).toByte()

        try {
            cipher.decrypt(ciphertext, creds.masterKey)
            fail("Decryption of tampered ciphertext should throw AEADBadTagException")
        } catch (e: Exception) {
            // Expected exception due to auth tag verification failure
            assertTrue(e is javax.crypto.AEADBadTagException || e.cause is javax.crypto.AEADBadTagException)
        }
    }

    @Test
    fun testMemoryZeroizer() {
        val sensitiveBytes = byteArrayOf(1, 2, 3, 4, 5)
        MemoryZeroizer.zeroize(sensitiveBytes)
        for (b in sensitiveBytes) {
            assertEquals(0.toByte(), b)
        }

        val sensitiveChars = charArrayOf('s', 'e', 'c', 'r', 'e', 't')
        MemoryZeroizer.zeroize(sensitiveChars)
        for (c in sensitiveChars) {
            assertEquals('\u0000', c)
        }
    }
}
