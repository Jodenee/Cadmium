from tqdm.asyncio import tqdm

from core.custom_types import Configuration

from ..enums import Colours

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

    def on_progress(self, file_number: int):
        self._progress_bar.n = file_number
        self._progress_bar.refresh()

    def close(self):
        self._progress_bar.close()