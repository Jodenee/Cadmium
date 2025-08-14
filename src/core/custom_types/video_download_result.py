from pathlib import Path
from typing import Optional, TypedDict


class VideoDownloadResult(TypedDict):
    success: bool
    youtube_video_title: str
    download_path: Optional[Path]
    error_message: Optional[str]
    