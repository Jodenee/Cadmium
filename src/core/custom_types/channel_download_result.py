from typing import List, Optional, TypedDict
from pathlib import Path

from .failed_download_information import FailedDownloadInformation

class ChannelDownloadResult(TypedDict):
    success: bool
    channel_name: str
    download_directory_path: Optional[Path]
    failed_downloads: List[FailedDownloadInformation]
    