package com.yourbrowser.app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.io.File

data class VaultFileItem(
    val file: File,
    val name: String,
    val sizeStr: String,
    val format: String
)

class VaultMediaAdapter(
    private val onItemClick: (VaultFileItem) -> Unit = {},
    private val onExportClick: (VaultFileItem) -> Unit,
    private val onDeleteClick: (VaultFileItem) -> Unit
) : RecyclerView.Adapter<VaultMediaAdapter.ViewHolder>() {

    private var items: List<VaultFileItem> = emptyList()

    fun submitList(newItems: List<VaultFileItem>) {
        items = newItems
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_vault_download, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvName: TextView = itemView.findViewById(R.id.tvVaultFileName)
        private val tvFormat: TextView = itemView.findViewById(R.id.tvVaultFileFormat)
        private val tvSize: TextView = itemView.findViewById(R.id.tvVaultFileSize)
        private val btnExport: Button = itemView.findViewById(R.id.btnExportFile)
        private val btnDelete: ImageButton = itemView.findViewById(R.id.btnDeleteVaultFile)

        fun bind(item: VaultFileItem) {
            tvName.text = item.name
            tvFormat.text = item.format
            tvSize.text = item.sizeStr

            itemView.setOnClickListener {
                onItemClick(item)
            }

            btnExport.setOnClickListener {
                onExportClick(item)
            }

            btnDelete.setOnClickListener {
                onDeleteClick(item)
            }
        }
    }
}
