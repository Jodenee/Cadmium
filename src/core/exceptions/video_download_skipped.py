class VideoDownloadSkipped(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
