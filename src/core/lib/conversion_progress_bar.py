import logging

from tqdm.asyncio import tqdm
from ffmpeg import Progress

from ..custom_types import Configuration
from ..enums import Colours
from ..utilities.constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class ConversionProgressBar:
    def __init__(self, description: str, stream_duration_in_ms: int, configuration: Configuration) -> None:
        custom_colour = configuration["ui_configuration"]["custom_convert_bar_colour"]

        print() # print new line before progress bar
        self._progress_bar: tqdm = tqdm(
            desc=description,
            total=round(stream_duration_in_ms / 1000, 2), 
            colour=custom_colour if custom_colour and len(custom_colour) > 0 else Colours.CADMIUM_ORANGE.value, 
            unit="seconds"
        )

        logger.info("initialised conversion progress bar (0/%s)", self._progress_bar.total)


    def on_progress(self, progress: Progress):
        self._progress_bar.n = min(round(progress.time.total_seconds(), 2), self._progress_bar.total)
        self._progress_bar.refresh()


    def close(self):
        self._progress_bar.n = self._progress_bar.total
        self._progress_bar.refresh()
        self._progress_bar.close()

        logger.info("closed conversion progress bar (%s/%s)", self._progress_bar.n, self._progress_bar.total)