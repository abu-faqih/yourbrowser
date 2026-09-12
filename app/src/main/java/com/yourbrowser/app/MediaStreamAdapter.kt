package com.yourbrowser.app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.yourbrowser.feature.downloader.model.DetectedMediaStream

class MediaStreamAdapter(
    private val onDownloadClick: (DetectedMediaStream) -> Unit
) : RecyclerView.Adapter<MediaStreamAdapter.ViewHolder>() {

    private var items: List<DetectedMediaStream> = emptyList()

    fun submitList(newItems: List<DetectedMediaStream>) {
        items = newItems
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_media_stream, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvTitle: TextView = itemView.findViewById(R.id.tvStreamTitle)
        private val tvFormat: TextView = itemView.findViewById(R.id.tvStreamFormat)
        private val btnDownload: Button = itemView.findViewById(R.id.btnDownloadStream)

        fun bind(stream: DetectedMediaStream) {
            tvTitle.text = stream.title
            tvFormat.text = "${stream.format.name} (${stream.mimeType})"
            btnDownload.setOnClickListener {
                onDownloadClick(stream)
            }
        }
    }
}
