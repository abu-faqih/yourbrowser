package com.yourbrowser.app.ui

import android.app.Dialog
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.yourbrowser.app.R
import com.yourbrowser.app.core.BrowserDataManager

class DataPanelDialog(
    context: Context,
    private val dataManager: BrowserDataManager,
    private val onUrlSelected: (String) -> Unit
) : Dialog(context) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestWindowFeature(Window.FEATURE_NO_TITLE)
        setContentView(R.layout.dialog_bookmarks_history)
        window?.setBackgroundDrawableResource(android.R.color.transparent)
        window?.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)

        val recycler = findViewById<RecyclerView>(R.id.recycler_data)
        recycler.layoutManager = LinearLayoutManager(context)

        fun refreshList() {
            val bookmarks = dataManager.getBookmarks().map { "★ " + it.title to it.url }
            val history = dataManager.getHistory().map { "⏱ " + it.title to it.url }
            val combined = bookmarks + history

            recycler.adapter = object : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
                override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
                    val tv = TextView(parent.context).apply {
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.WRAP_CONTENT
                        )
                        setPadding(24, 20, 24, 20)
                        setTextColor(context.getColor(R.color.text_primary))
                        textSize = 14f
                        setBackgroundResource(R.drawable.bg_pill_secondary)
                    }
                    val container = android.widget.FrameLayout(parent.context).apply {
                        setPadding(0, 4, 0, 4)
                        addView(tv)
                    }
                    return object : RecyclerView.ViewHolder(container) {}
                }

                override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
                    val item = combined[position]
                    val container = holder.itemView as android.widget.FrameLayout
                    val tv = container.getChildAt(0) as TextView
                    tv.text = "${item.first}\n${item.second}"
                    tv.setOnClickListener {
                        onUrlSelected(item.second)
                        dismiss()
                    }
                }

                override fun getItemCount(): Int = combined.size
            }
        }

        refreshList()

        findViewById<Button>(R.id.btn_clear_data).setOnClickListener {
            dataManager.clearHistory()
            refreshList()
        }
    }
}
