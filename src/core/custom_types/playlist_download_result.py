from typing import List, Optional, Tuple, TypedDict
from pathlib import Path

from .failed_download_information import FailedDownloadInformation

class PlaylistDownloadResult(TypedDict):
    success: bool
    playlist_name: str
    download_directory_path: Optional[Path]
    failed_downloads: List[FailedDownloadInformation]
    