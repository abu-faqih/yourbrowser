package com.yourbrowser.app.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.yourbrowser.app.R
import com.yourbrowser.app.model.BrowserTab

class TabsAdapter(
    private val tabs: List<BrowserTab>,
    private val activeTabId: String,
    private val onTabSelected: (BrowserTab) -> Unit,
    private val onTabClosed: (BrowserTab) -> Unit,
    private val onLockToggle: (BrowserTab) -> Unit
) : RecyclerView.Adapter<TabsAdapter.TabViewHolder>() {

    class TabViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.txt_tab_item_title)
        val url: TextView = view.findViewById(R.id.txt_tab_item_url)
        val btnClose: ImageView = view.findViewById(R.id.btn_tab_close)
        val btnLock: ImageView = view.findViewById(R.id.btn_lock_toggle)
        val imgIcon: ImageView = view.findViewById(R.id.img_tab_icon)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TabViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_tab, parent, false)
        return TabViewHolder(view)
    }

    override fun onBindViewHolder(holder: TabViewHolder, position: Int) {
        val tab = tabs[position]
        holder.title.text = if (tab.isLocked && !tab.isCurrentSessionUnlocked) "🔒 Encrypted Tab" else tab.title
        holder.url.text = if (tab.isLocked && !tab.isCurrentSessionUnlocked) "Protected session" else tab.url

        if (tab.id == activeTabId) {
            holder.itemView.setBackgroundResource(R.drawable.bg_dialog_card)
        } else {
            holder.itemView.setBackgroundResource(R.drawable.bg_omnibox)
        }

        if (tab.isLocked) {
            holder.btnLock.setImageResource(R.drawable.ic_lock)
            holder.btnLock.setColorFilter(holder.itemView.context.getColor(R.color.accent_cyan))
        } else {
            holder.btnLock.setImageResource(R.drawable.ic_lock)
            holder.btnLock.setColorFilter(holder.itemView.context.getColor(R.color.text_secondary))
        }

        holder.itemView.setOnClickListener { onTabSelected(tab) }
        holder.btnClose.setOnClickListener { onTabClosed(tab) }
        holder.btnLock.setOnClickListener { onLockToggle(tab) }
    }

    override fun getItemCount(): Int = tabs.size
}
