from pathlib import Path

class VideoConversionSkipped(Exception):
    def __init__(self, youtube_video_title: str, path: Path) -> None:
        super().__init__(f"YouTube video: ({youtube_video_title}) has not been converted as it already exists in ({path}).")