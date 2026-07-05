from typing import Optional, TypedDict
from pathlib import Path

from core.custom_types.video_download_result import VideoDownloadResult

class CollectionDownloadResult(TypedDict):
    success: bool
    collection_type: str
    collection_name: str
    download_directory_path: Optional[Path]
    failed_downloads: list[VideoDownloadResult]
