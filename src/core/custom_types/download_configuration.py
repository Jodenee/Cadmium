from pathlib import Path
from typing import Optional, TypedDict

class DownloadConfiguration(TypedDict):
    use_download_location_override: bool
    download_location_override: Optional[str]
    default_download_location: Path
