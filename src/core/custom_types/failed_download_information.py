from typing import TypedDict

class FailedDownloadInformation(TypedDict):
    youtube_video_title: str
    youtube_video_url: str
    error_message: str
    