from pathlib import Path

class VideoDownloadSkipped(Exception):
    def __init__(self, youtube_video_title: str, path: Path) -> None:
        super().__init__(f"YouTube video: ({youtube_video_title}) has not been downloaded as it already exists in ({path}).")