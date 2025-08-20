from pathlib import Path

from tqdm.asyncio import tqdm

from core.custom_types import Configuration

from ..enums import Colours

class ClearDirectoryDisplay:
    def __init__(self, description: str, total_files: int, configuration: Configuration) -> None:
        custom_colour = configuration["ui_configuration"]["custom_clear_directory_bar_colour"]

        print() # print new line before progress bar
        self.progress_bar: tqdm = tqdm(
            desc=description, 
            total=total_files, 
            colour=custom_colour if custom_colour and len(custom_colour) > 0 else Colours.CADMIUM_YELLOW.value, 
            unit="file"
        )

    def on_progress(self, file_number: int):
        self.progress_bar.n = file_number
        self.progress_bar.refresh()
