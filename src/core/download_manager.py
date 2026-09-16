"""
Download Manager Module
Handles Chromium QWebEngineDownloadRequest interception, progress tracking,
and downloads queue state.
"""

import os
import time
import uuid
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~/Downloads")


class DownloadItemState:
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class DownloadTracker(QObject):
    """Tracks an active or historical download item."""

    updated = pyqtSignal(str)  # Emits item_id on progress/state change

    def __init__(self, download_id: str, download_req: Optional[QWebEngineDownloadRequest] = None, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.download_req = download_req
        self.filename = ""
        self.save_path = ""
        self.url = ""
        self.received_bytes = 0
        self.total_bytes = 0
        self.state = DownloadItemState.IN_PROGRESS
        self.start_time = time.time()

        if download_req:
            self.filename = os.path.basename(download_req.downloadFileName()) or "download"
            self.save_path = download_req.downloadDirectory() + os.sep + self.filename
            self.url = download_req.url().toString()
            self.total_bytes = download_req.totalBytes()
            self.received_bytes = download_req.receivedBytes()

            # Connect signals
            download_req.receivedBytesChanged.connect(self._on_bytes_changed)
            download_req.totalBytesChanged.connect(self._on_total_bytes_changed)
            download_req.stateChanged.connect(self._on_state_changed)

    def _on_bytes_changed(self):
        if self.download_req:
            self.received_bytes = self.download_req.receivedBytes()
            self.updated.emit(self.download_id)

    def _on_total_bytes_changed(self):
        if self.download_req:
            self.total_bytes = self.download_req.totalBytes()
            self.updated.emit(self.download_id)

    def _on_state_changed(self, state):
        if not self.download_req:
            return
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.state = DownloadItemState.COMPLETED
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.state = DownloadItemState.CANCELLED
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            self.state = DownloadItemState.INTERRUPTED
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
            self.state = DownloadItemState.IN_PROGRESS

        self.updated.emit(self.download_id)

    def cancel(self):
        if self.download_req and self.state == DownloadItemState.IN_PROGRESS:
            self.download_req.cancel()
            self.state = DownloadItemState.CANCELLED
            self.updated.emit(self.download_id)

    @property
    def percentage(self) -> int:
        if self.total_bytes <= 0:
            return 0
        return int((self.received_bytes / self.total_bytes) * 100)


class DownloadManager(QObject):
    """Coordinates download requests across browser tabs."""

    download_started = pyqtSignal(DownloadTracker)
    download_updated = pyqtSignal(str)

    def __init__(self, download_dir: str = DEFAULT_DOWNLOAD_DIR, parent=None):
        super().__init__(parent)
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.downloads: List[DownloadTracker] = []

    def handle_download_request(self, download_item: QWebEngineDownloadRequest) -> DownloadTracker:
        """Processes an incoming QWebEngine download request and starts file transfer."""
        suggested_filename = download_item.downloadFileName() or "download"
        base_name, ext = os.path.splitext(suggested_filename)
        dest_path = os.path.join(self.download_dir, suggested_filename)

        # Handle duplicate filenames nicely
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(self.download_dir, f"{base_name} ({counter}){ext}")
            counter += 1

        final_filename = os.path.basename(dest_path)
        download_item.setDownloadDirectory(self.download_dir)
        download_item.setDownloadFileName(final_filename)

        tracker = DownloadTracker(str(uuid.uuid4()), download_item, self)
        tracker.filename = final_filename
        tracker.save_path = dest_path
        tracker.updated.connect(lambda d_id: self.download_updated.emit(d_id))

        self.downloads.insert(0, tracker)
        download_item.accept()

        self.download_started.emit(tracker)
        return tracker

    def get_all_downloads(self) -> List[DownloadTracker]:
        return list(self.downloads)

    def clear_finished(self):
        """Remove completed or cancelled downloads from the memory list."""
        self.downloads = [d for d in self.downloads if d.state == DownloadItemState.IN_PROGRESS]
