from pytubefix.async_youtube import AsyncYouTube

from ..progress_bars import ClearDirectoryProgressBar, ConversionProgressBar, DownloadProgressBar
from ...custom_types import Configuration

class ProgressBarFactory:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration: Configuration = configuration

    def clear_directory(self, description: str, total_files: int) -> ClearDirectoryProgressBar:
        return ClearDirectoryProgressBar(description, total_files, self.configuration)
    
    def conversion(
        self,
        description: str,
        stream_duration_in_ms: int,
    ) -> ConversionProgressBar:
        return ConversionProgressBar(description, stream_duration_in_ms, self.configuration)
    
    def download(self, description: str, stream_size_in_bytes: int, youtube_video: AsyncYouTube) -> DownloadProgressBar:
        return DownloadProgressBar(description, stream_size_in_bytes, youtube_video, self.configuration)
