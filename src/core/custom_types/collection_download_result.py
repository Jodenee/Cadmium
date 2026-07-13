from typing import Optional, TypedDict
from pathlib import Path

from .video_download_result import VideoDownloadResultFailure

class CollectionDownloadResult(TypedDict):
    success: bool
    collection_type: str
    collection_name: str
    download_directory_path: Optional[Path]
    failed_downloads: list[VideoDownloadResultFailure]
