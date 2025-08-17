from pathlib import Path

from tqdm import tqdm

from ..enums import Colours

class ClearDirectoryDisplay:
    def __init__(self, directory: Path, total_files: int) -> None:
        self.progress_bar: tqdm = tqdm(
            desc=f"Clearing ({directory})", 
            total=total_files, 
            colour=Colours.CADMIUM_YELLOW.value, 
            unit="file"
        )
        self.directory = directory

    def on_progress(self, file_number: int):
        self.progress_bar.n = file_number
        self.progress_bar.refresh()
