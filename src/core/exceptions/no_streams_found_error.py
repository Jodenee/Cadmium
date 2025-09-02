class NoStreamsFoundError(Exception):
    def __init__(self, youtube_video_title: str) -> None:
        super().__init__(f"YouTube video: ({youtube_video_title}) has no streams.")
