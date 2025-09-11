from pathlib import Path

class ImpossibleDownloadPath(Exception):
    def __init__(self, path: Path) -> None:
        super().__init__(f"Cannot download media to ({path}) due to hitting the system's path length limit. Try shortening the name of the folder or picking another.")
