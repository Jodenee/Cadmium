from typing import List, Optional, TypedDict

from pytubefix import YouTube
from pathlib import Path

class PlaylistDownloadResult(TypedDict):
    success: bool
    playlist_name: str
    download_directory_path: Optional[Path]
    failed_downloads: List[str]
    error_message: Optional[str]
    