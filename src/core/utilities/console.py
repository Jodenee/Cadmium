from typing import List, Optional

from core.custom_types.failed_download_information import FailedDownloadInformation

def spaced_print(*objects, sep: Optional[str] = "", flush: bool = False, end: Optional[str] = None) -> None:
    print(*("\n", *objects), sep=sep, flush=flush, end=end)

def print_failed_downloads(failed_downloads: List[FailedDownloadInformation]):
    failed_download_info = [
        f"{download_failure_info['youtube_video_title']} ({download_failure_info['youtube_video_url']})\nReason: \"{download_failure_info['error_message']}\"" 
        for download_failure_info in failed_downloads 
    ]

    spaced_print(str.join("\n\n", failed_download_info))
