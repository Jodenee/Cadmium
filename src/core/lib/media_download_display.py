from pytubefix.async_youtube import Stream

from tqdm.asyncio import tqdm

from core.custom_types.configuration import Configuration
from ..enums import Colours

class MediaDownloadDisplay:
    def __init__(self, description: str, stream_size_in_bytes: int, configuration: Configuration) -> None:
        custom_colour = configuration["ui_configuration"]["custom_download_bar_colour"]
        
        print() # print new line before progress bar
        self.progress_bar: tqdm = tqdm(
            desc=description, 
            total=stream_size_in_bytes, 
            colour=custom_colour if custom_colour and len(custom_colour) > 0 else Colours.CADMIUM_RED.value, 
            unit="B",
            unit_scale=True, 
            unit_divisor=1024
        )

    def show_progress_callback(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        total_file_size: int = stream.filesize
        total_bytes_downloaded: int = total_file_size - bytes_remaining

        self.progress_bar.n = total_bytes_downloaded
        self.progress_bar.refresh()
