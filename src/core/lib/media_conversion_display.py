from typing import Optional

from pytubefix.async_youtube import Stream
from tqdm.asyncio import tqdm
from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress

from core.custom_types import Configuration

from ..enums import Colours

class MediaConversionDisplay:
    def __init__(self, description: str, stream: Stream, ffmpeg: FFmpeg, configuration: Configuration) -> None:
        custom_colour = configuration["ui_configuration"]["custom_convert_bar_colour"]

        print() # print new line before progress bar
        self.progress_bar: tqdm = tqdm(
            desc=description,
            total=round(int(stream.durationMs) / 1000, 2), 
            colour=custom_colour if custom_colour and len(custom_colour) > 0 else Colours.CADMIUM_ORANGE.value, 
            unit="seconds"
        )
        self.ffmpeg = ffmpeg

    def on_progress(self, progress: Progress):
        self.progress_bar.n = min(round(progress.time.total_seconds(), 2), self.progress_bar.total)
        self.progress_bar.refresh()