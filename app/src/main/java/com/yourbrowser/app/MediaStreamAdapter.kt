package com.yourbrowser.app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.yourbrowser.feature.downloader.model.DetectedMediaStream
import com.yourbrowser.feature.downloader.model.StreamFormat

class MediaStreamAdapter(
    private val onPlayClick: (DetectedMediaStream) -> Unit = {},
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
        private val tvResolutionBadge: TextView = itemView.findViewById(R.id.tvResolutionBadge)
        private val tvTitle: TextView = itemView.findViewById(R.id.tvStreamTitle)
        private val tvEstimatedSize: TextView = itemView.findViewById(R.id.tvEstimatedSize)
        private val tvFormat: TextView = itemView.findViewById(R.id.tvStreamFormat)
        private val btnPlay: Button = itemView.findViewById(R.id.btnPlayStream)
        private val btnDownload: Button = itemView.findViewById(R.id.btnDownloadStream)

        fun bind(stream: DetectedMediaStream) {
            tvTitle.text = stream.title.ifEmpty { "Video Stream" }

            btnPlay.setOnClickListener {
                onPlayClick(stream)
            }

            when (stream.format) {
                StreamFormat.HLS_M3U8 -> {
                    tvResolutionBadge.text = stream.resolution ?: "1080p FHD"
                    tvEstimatedSize.text = if (stream.sizeBytes > 0) "${stream.sizeBytes / (1024 * 1024)} MB" else "~145 MB"
                    tvFormat.text = "HLS Master Playlist • Video AVC/H.264"
                }
                StreamFormat.DASH_MPD -> {
                    tvResolutionBadge.text = stream.resolution ?: "720p HD"
                    tvEstimatedSize.text = if (stream.sizeBytes > 0) "${stream.sizeBytes / (1024 * 1024)} MB" else "~80 MB"
                    tvFormat.text = "MPEG-DASH Stream • AVC/AAC"
                }
                StreamFormat.DIRECT_MP4 -> {
                    tvResolutionBadge.text = stream.resolution ?: "DIRECT MP4"
                    tvEstimatedSize.text = if (stream.sizeBytes > 0) "${stream.sizeBytes / (1024 * 1024)} MB" else "Direct File"
                    tvFormat.text = "MP4 Direct Download Container"
                }
                StreamFormat.DIRECT_WEBM -> {
                    tvResolutionBadge.text = stream.resolution ?: "WEBM"
                    tvEstimatedSize.text = if (stream.sizeBytes > 0) "${stream.sizeBytes / (1024 * 1024)} MB" else "Direct File"
                    tvFormat.text = "WebM Direct Stream Container"
                }
                StreamFormat.BLOB_MSE -> {
                    tvResolutionBadge.text = "MSE BLOB"
                    tvEstimatedSize.text = "Dynamic"
                    tvFormat.text = "MSE Media Source Extension Capture"
                }
                StreamFormat.UNKNOWN -> {
                    tvResolutionBadge.text = "STREAM"
                    tvEstimatedSize.text = "Unknown"
                    tvFormat.text = "Generic Media Stream"
                }
            }

            btnDownload.setOnClickListener {
                onDownloadClick(stream)
            }
        }
    }
}
