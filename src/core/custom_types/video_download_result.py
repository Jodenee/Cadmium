from pathlib import Path
from typing import Literal, TypedDict
from pytubefix import AsyncYouTube

class VideoDownloadResultSuccess(TypedDict):
    success: Literal[True]
    youtube_video_title: str
    stream_itags: tuple[int, ...]
    download_path: Path

class VideoDownloadResultFailure(TypedDict):
    success: Literal[False]
    by_user_action: bool
    youtube_video_title: str
    message: str

type VideoDownloadResult = VideoDownloadResultSuccess | VideoDownloadResultFailure
