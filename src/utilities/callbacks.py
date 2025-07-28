from utilities.console import spaced_print
from pytubefix import Stream
from math import floor

def video_download_progress_callback(stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
    total_file_size: int = stream.filesize
    total_bytes_downloaded: int = total_file_size - bytes_remaining
    percentage_completed: float = round((total_bytes_downloaded / total_file_size) * 100, 2)
    megabytes_downloaded: int = floor(len(chunk) / 1_000_000)

    spaced_print(f"Video ({stream.title}) is {percentage_completed}% complete... ({megabytes_downloaded}Mbp/s)")
