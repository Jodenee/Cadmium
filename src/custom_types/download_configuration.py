from pathlib import Path
from typing import Optional, ReadOnly, TypedDict

class DownloadConfiguration(TypedDict):
    use_custom_download_location: ReadOnly[bool]
    custom_download_location: ReadOnly[Optional[str]]
    default_download_location: ReadOnly[Path]
