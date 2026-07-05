import logging

from pytubefix.async_youtube import AsyncYouTube, Stream
from tqdm.asyncio import tqdm

from ...custom_types.configuration import Configuration
from ...enums import Colours
from ...utilities.constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class DownloadProgressBar:
    def __init__(self, description: str, stream_size_in_bytes: int, youtube_video: AsyncYouTube, configuration: Configuration) -> None:
        custom_colour = configuration["ui_configuration"]["custom_download_bar_colour"]
        bar_colour = custom_colour if custom_colour and len(custom_colour) > 0 else Colours.CADMIUM_RED.value
        
        print() # print new line before progress bar
        self._progress_bar: tqdm = tqdm(
            desc=description, 
            total=stream_size_in_bytes, 
            colour=bar_colour, 
            unit="B",
            unit_scale=True, 
            unit_divisor=1024
        )

        youtube_video.register_on_progress_callback(self.on_progress)
        logger.info("initialised download progress bar (0/%s)", self._progress_bar.total)


    def on_progress(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        total_file_size: int = stream.filesize
        total_bytes_downloaded: int = total_file_size - bytes_remaining

        self._progress_bar.n = total_bytes_downloaded
        self._progress_bar.refresh()

    def close(self):
        self._progress_bar.n = self._progress_bar.total
        self._progress_bar.refresh()
        self._progress_bar.close()

        logger.info("closed download progress bar (%s/%s)", self._progress_bar.n, self._progress_bar.total)
