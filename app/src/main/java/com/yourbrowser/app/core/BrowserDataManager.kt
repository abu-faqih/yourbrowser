package com.yourbrowser.app.core

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONObject

data class BookmarkItem(val id: String, val title: String, val url: String, val createdAt: Long)
data class HistoryItem(val id: String, val title: String, val url: String, val timestamp: Long)

class BrowserDataManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("yourbrowser_data", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_BOOKMARKS = "key_bookmarks"
        private const val KEY_HISTORY = "key_history"
        private const val KEY_SEARCH_ENGINE = "key_search_engine"
    }

    // --- Bookmarks ---
    fun getBookmarks(): List<BookmarkItem> {
        val raw = prefs.getString(KEY_BOOKMARKS, "[]") ?: "[]"
        val array = JSONArray(raw)
        val list = mutableListOf<BookmarkItem>()
        for (i in 0 until array.length()) {
            val obj = array.getJSONObject(i)
            list.add(
                BookmarkItem(
                    id = obj.optString("id", System.currentTimeMillis().toString()),
                    title = obj.optString("title", "Bookmark"),
                    url = obj.optString("url", ""),
                    createdAt = obj.optLong("createdAt", System.currentTimeMillis())
                )
            )
        }
        return list
    }

    fun addBookmark(title: String, url: String): BookmarkItem {
        val current = getBookmarks().toMutableList()
        val existingIndex = current.indexOfFirst { it.url == url }
        val item = BookmarkItem(
            id = System.currentTimeMillis().toString(),
            title = if (title.isBlank()) url else title,
            url = url,
            createdAt = System.currentTimeMillis()
        )
        if (existingIndex >= 0) {
            current[existingIndex] = item
        } else {
            current.add(0, item)
        }
        saveBookmarks(current)
        return item
    }

    fun removeBookmark(url: String): Boolean {
        val current = getBookmarks().toMutableList()
        val removed = current.removeAll { it.url == url }
        if (removed) {
            saveBookmarks(current)
        }
        return removed
    }

    fun isBookmarked(url: String): Boolean {
        if (url.isBlank()) return false
        return getBookmarks().any { it.url == url }
    }

    private fun saveBookmarks(items: List<BookmarkItem>) {
        val array = JSONArray()
        items.forEach {
            val obj = JSONObject()
            obj.put("id", it.id)
            obj.put("title", it.title)
            obj.put("url", it.url)
            obj.put("createdAt", it.createdAt)
            array.put(obj)
        }
        prefs.edit().putString(KEY_BOOKMARKS, array.toString()).apply()
    }

    // --- History ---
    fun getHistory(): List<HistoryItem> {
        val raw = prefs.getString(KEY_HISTORY, "[]") ?: "[]"
        val array = JSONArray(raw)
        val list = mutableListOf<HistoryItem>()
        for (i in 0 until array.length()) {
            val obj = array.getJSONObject(i)
            list.add(
                HistoryItem(
                    id = obj.optString("id", System.currentTimeMillis().toString()),
                    title = obj.optString("title", "Page"),
                    url = obj.optString("url", ""),
                    timestamp = obj.optLong("timestamp", System.currentTimeMillis())
                )
            )
        }
        return list
    }

    fun addHistory(title: String, url: String) {
        if (url.isBlank() || url.startsWith("about:") || url.startsWith("data:")) return
        val current = getHistory().toMutableList()
        // Deduplicate recent same url
        current.removeAll { it.url == url }
        current.add(0, HistoryItem(
            id = System.currentTimeMillis().toString(),
            title = if (title.isBlank()) url else title,
            url = url,
            timestamp = System.currentTimeMillis()
        ))
        // Cap history at 500 entries
        val trimmed = if (current.size > 500) current.take(500) else current
        val array = JSONArray()
        trimmed.forEach {
            val obj = JSONObject()
            obj.put("id", it.id)
            obj.put("title", it.title)
            obj.put("url", it.url)
            obj.put("timestamp", it.timestamp)
            array.put(obj)
        }
        prefs.edit().putString(KEY_HISTORY, array.toString()).apply()
    }

    fun clearHistory() {
        prefs.edit().remove(KEY_HISTORY).apply()
    }

    // --- Search Engine ---
    fun formatSearchQuery(input: String): String {
        val trimmed = input.trim()
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            return trimmed
        }
        if (trimmed.contains(".") && !trimmed.contains(" ")) {
            return "https://$trimmed"
        }
        val encoded = java.net.URLEncoder.encode(trimmed, "UTF-8")
        return "https://search.brave.com/search?q=$encoded"
    }
}
