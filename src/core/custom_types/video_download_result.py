from pathlib import Path
from typing import Literal, TypedDict
from pytubefix import AsyncYouTube

class VideoDownloadResultSuccess(TypedDict):
    success: Literal[True]
    youtube_video: AsyncYouTube
    download_path: Path

class VideoDownloadResultFailure(TypedDict):
    success: Literal[False]
    by_user_action: bool
    youtube_video: AsyncYouTube
    message: str

type VideoDownloadResult = VideoDownloadResultSuccess | VideoDownloadResultFailure
