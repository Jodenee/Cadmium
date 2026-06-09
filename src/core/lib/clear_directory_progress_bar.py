import logging

from tqdm.asyncio import tqdm

from ..custom_types import Configuration
from ..enums import Colours
from ..utilities.constants import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

class ClearDirectoryProgressBar:
    def __init__(self, description: str, total_files: int, configuration: Configuration) -> None:
        custom_bar_colour = configuration["ui_configuration"]["custom_clear_directory_bar_colour"]
        bar_colour = custom_bar_colour if custom_bar_colour and len(custom_bar_colour) > 0 else Colours.CADMIUM_YELLOW.value

        print() # print new line before progress bar
        self._progress_bar: tqdm = tqdm(
            desc=description, 
            total=total_files, 
            colour=bar_colour, 
            unit="file"
        )

        logger.debug("initialise clear directory progress bar total=%s", self._progress_bar.total)

    def on_progress(self, file_number: int):
        self._progress_bar.n = file_number
        self._progress_bar.refresh()

        logger.debug("clear directory progress total_size=%s current_size=%s", self._progress_bar.total, self._progress_bar.n)

    def close(self):
        self._progress_bar.close()

        logger.debug("closed clear directory progress bar total_size=%s current_size=%s", self._progress_bar.total, self._progress_bar.n)