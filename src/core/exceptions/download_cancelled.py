class DownloadCancelled(Exception):
    def __init__(self, youtube_video_title: str) -> None:
        super().__init__(f"Video ({youtube_video_title}) download has been cancelled.")
