package com.yourbrowser.app.core

import java.security.MessageDigest

object SecurityVault {

    private const val SALT = "yourbrowser_secure_salt_2026"

    fun hashPassword(password: String): String {
        val bytes = (SALT + password).toByteArray(Charsets.UTF_8)
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(bytes)
        return digest.joinToString("") { "%02x".format(it) }
    }

    fun verifyPassword(candidate: String, expectedHash: String): Boolean {
        if (expectedHash.isBlank()) return true
        return hashPassword(candidate) == expectedHash
    }
}
