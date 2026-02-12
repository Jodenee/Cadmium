from pathlib import Path
from typing import Union

class ImpossibleDownloadPath(Exception):
    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(f"Cannot download media to ({path}) due to hitting the operating system's path length limit. Try shortening the name of the folder or picking another.")
