package com.yourbrowser.app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

data class BrowserTab(
    val id: String,
    var title: String,
    var url: String,
    var isActive: Boolean = false
)

class TabAdapter(
    private val onTabClick: (BrowserTab) -> Unit,
    private val onCloseClick: (BrowserTab) -> Unit
) : RecyclerView.Adapter<TabAdapter.ViewHolder>() {

    private var items: List<BrowserTab> = emptyList()

    fun submitList(newItems: List<BrowserTab>) {
        items = newItems
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_tab_card, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvTitle: TextView = itemView.findViewById(R.id.tvTabTitle)
        private val tvUrl: TextView = itemView.findViewById(R.id.tvTabUrl)
        private val tvActiveStatus: TextView = itemView.findViewById(R.id.tvTabActiveStatus)
        private val btnClose: ImageButton = itemView.findViewById(R.id.btnCloseTab)

        fun bind(tab: BrowserTab) {
            tvTitle.text = tab.title.ifEmpty { "New Tab" }
            tvUrl.text = tab.url.ifEmpty { "about:blank" }

            if (tab.isActive) {
                tvActiveStatus.visibility = View.VISIBLE
                tvActiveStatus.text = "ACTIVE"
            } else {
                tvActiveStatus.visibility = View.GONE
            }

            itemView.setOnClickListener {
                onTabClick(tab)
            }

            btnClose.setOnClickListener {
                onCloseClick(tab)
            }
        }
    }
}
