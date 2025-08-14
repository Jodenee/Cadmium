from typing import Optional

from pytubefix import Stream
from tqdm import tqdm
from ffmpeg import FFmpeg, Progress

from ..enums import Colours

class MediaConversionDisplay:
    def __init__(self, stream: Stream, ffmpeg: FFmpeg, custom_description: Optional[str] = None) -> None:
        self.progress_bar: tqdm = tqdm(
            desc=f"Converting ({stream.title})" if custom_description == None else custom_description, 
            total=round(int(stream.durationMs) / 1000, 2), 
            colour=Colours.CADMIUM_ORANGE.value, 
            unit="seconds"
        )
        self.ffmpeg = ffmpeg

    def on_progress(self, progress: Progress):
        self.progress_bar.n = min(round(progress.time.total_seconds(), 2), self.progress_bar.total)
        self.progress_bar.refresh()