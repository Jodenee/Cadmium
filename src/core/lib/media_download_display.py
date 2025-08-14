from typing import Optional
from pytubefix import YouTube, Stream

from tqdm import tqdm
from ..enums import Colours

class MediaDownloadDisplay:
    def __init__(self, youtube_video: YouTube, stream_size_in_bytes: int, custom_description: Optional[str] = None) -> None:
        self.progress_bar: tqdm = tqdm(
            desc=f"Downloading ({youtube_video.title})" if custom_description == None else custom_description, 
            total=stream_size_in_bytes, 
            colour=Colours.CADMIUM_RED, 
            unit="B",
            unit_scale=True, 
            unit_divisor=1024
        )

    def show_progress_callback(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        total_file_size: int = stream.filesize
        total_bytes_downloaded: int = total_file_size - bytes_remaining

        self.progress_bar.n = total_bytes_downloaded
        self.progress_bar.refresh()

