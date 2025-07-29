from pathlib import Path
from typing import Optional, TypedDict

class DownloadConfiguration(TypedDict):
    use_custom_download_location: bool
    custom_download_location: Optional[str]
    default_download_location: Path
