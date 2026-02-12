from typing import Callable, List, Optional, Tuple, Union, cast
from pick import Option, pick
from pytubefix.async_youtube import Stream, StreamQuery

from core.utilities.constants import SELECT_MENU_INDICATOR
from core.utilities.pytubefix_extensions import stream_repr

from ..custom_types.failed_download_information import FailedDownloadInformation

# Functions

def spaced_print(*objects, sep: Optional[str] = "", flush: bool = False, end: Optional[str] = None) -> None:
    print(*("\n", *objects), sep=sep, flush=flush, end=end)



def print_failed_downloads(failed_downloads: List[FailedDownloadInformation]):
    failed_download_info = [
        f"{download_failure_info['youtube_video_title']} ({download_failure_info['youtube_video_url']})\nReason: \"{download_failure_info['error_message']}\"" 
        for download_failure_info in failed_downloads 
    ]

    spaced_print(str.join("\n\n", failed_download_info))



def pick_from_streams(streams: StreamQuery, label_generator: Optional[Callable[[Stream], str]] = None) -> List[Stream]:
    options = [ 
        Option(
            f"stream {stream.itag}" if not label_generator else label_generator(stream),
            stream, 
            stream_repr(stream)
        ) for stream in streams 
    ]
    stream_pick_menu = cast(List[Tuple[Option, int]], pick(
        options, 
        "Pick the streams you wish to download. [Spacebar] to select/deselect and [Enter] to download.", 
        indicator=SELECT_MENU_INDICATOR, 
        multiselect=True,
        min_selection_count=1
    ))

    return cast(List[Stream], [ picked_option[0].value for picked_option in stream_pick_menu ])
