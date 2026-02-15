from pathlib import Path
from typing import Optional, TypedDict
from pytubefix import AsyncYouTube

class VideoDownloadResult(TypedDict):
    success: bool
    youtube_video: AsyncYouTube
    download_path: Optional[Path]
    error_message: Optional[str]
    