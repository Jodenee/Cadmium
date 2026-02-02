from ffmpeg.asyncio import FFmpeg
from pytubefix.async_youtube import AsyncYouTube, Stream

from ...custom_types import Configuration
from ...lib import ClearDirectoryProgressBar, ConversionProgressBar, DownloadProgressBar

class ProgressBarFactory:
    def __init__(self, configuration: Configuration) -> None:
        self.configuration: Configuration = configuration

    def clear_directory(self, description: str, total_files: int) -> ClearDirectoryProgressBar:
        return ClearDirectoryProgressBar(description, total_files, self.configuration)
    
    def conversion(
        self,
        description: str,
        stream: Stream,
        ffmpeg: FFmpeg,
    ) -> ConversionProgressBar:
        return ConversionProgressBar(description, stream, ffmpeg, self.configuration)
    
    def download(self, description: str, stream_size_in_bytes: int, youtube_video: AsyncYouTube) -> DownloadProgressBar:
        return DownloadProgressBar(description, stream_size_in_bytes, youtube_video, self.configuration)
