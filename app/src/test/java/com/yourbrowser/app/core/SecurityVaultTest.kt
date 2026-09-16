package com.yourbrowser.app.core

import org.junit.Assert.*
import org.junit.Test

class SecurityVaultTest {

    @Test
    fun testPasswordHashingConsistency() {
        val hash1 = SecurityVault.hashPassword("secret123")
        val hash2 = SecurityVault.hashPassword("secret123")
        assertEquals(hash1, hash2)
        assertNotEquals("secret123", hash1)
    }

    @Test
    fun testPasswordVerification() {
        val hash = SecurityVault.hashPassword("pass_abc")
        assertTrue(SecurityVault.verifyPassword("pass_abc", hash))
        assertFalse(SecurityVault.verifyPassword("wrong_pass", hash))
        assertTrue(SecurityVault.verifyPassword("anything", ""))
    }
}
