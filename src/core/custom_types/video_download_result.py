from pathlib import Path
from typing import Literal, Optional, TypedDict, Union
from pytubefix import AsyncYouTube

class VideoDownloadResultSuccess(TypedDict):
    success: Literal[True]
    youtube_video: AsyncYouTube
    download_path: Path
    error_message: None

class VideoDownloadResultFailure(TypedDict):
    success: Literal[False]
    youtube_video: AsyncYouTube
    download_path: None
    error_message: str

VideoDownloadResult = Union[VideoDownloadResultSuccess, VideoDownloadResultFailure]
