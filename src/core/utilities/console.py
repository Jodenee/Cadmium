import logging

from typing import Callable, List, Optional, Tuple, cast
from pick import Option, pick
from pytubefix.async_youtube import Stream, StreamQuery

from core.custom_types.collection_download_result import CollectionDownloadResult
from core.custom_types.video_download_result import VideoDownloadResult
from core.utilities.constants import SELECT_MENU_INDICATOR, APPLICATION_LOGGER_NAME
from core.utilities.pytubefix_extensions import stream_repr

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

# Functions

def spaced_print(*values, sep: Optional[str] = "", flush: bool = False, end: Optional[str] = None) -> None:
    """A wrapper for the built in `print` function to ensure output is spaced properly.

    Args:
        values:
            A `Tuple` of values to output.
        sep:
            `string` inserted between values, default an empty string.
        end:
            `string` appended after the last value, default a newline.
        flush:
            Whether to forcibly flush the stream.
    """

    print(*("\n", *values), sep=sep, flush=flush, end=end)


async def print_failed_downloads(failed_downloads: List[VideoDownloadResult]) -> None:
    """Prints failed download information in a user friendly format.

    Args:
        failed_downloads:
            A `List` of `VideoDownloadResult` to show the user.
    """

    information_text = []

    for failed_download in failed_downloads:
        video_title = await failed_download['youtube_video'].title()
        video_url = failed_download['youtube_video'].watch_url

        information_text.append(
            f"{video_title} ({video_url})\nReason: \"{failed_download['error_message']}\"" 
        )

    spaced_print(str.join("\n\n", information_text))


async def display_video_download_result(results: List[VideoDownloadResult]) -> None:
    """Prints the result of a video download in a user friendly format.

    Args:
        failed_downloads:
            A `List` of `VideoDownloadResult` to show the user.
    """

    for result in results:
        if result["success"]:
            spaced_print(f"Video ({await result['youtube_video'].title()}) was downloaded successfully! ({result['download_path']})")
        else:
            spaced_print(f"An error occurred while downloading Video ({await result['youtube_video'].title()}) {result['error_message']}")


async def display_collection_download_result(result: CollectionDownloadResult) -> None:
    """Prints the result of a collection download in a user friendly format.

    Args:
        result:
            A `CollectionDownloadResult` to show the user.
    """

    if result["success"]:
        spaced_print(f"{result['collection_type']} ({result['collection_name']}) was downloaded successfully! ({result['download_directory_path']})")
    else:
        spaced_print(f"An error occurred while downloading {result['collection_type']} ({result['collection_name']})")
        spaced_print(f"Failed to download the following:")

        await print_failed_downloads(result["failed_downloads"])


def pick_from_streams(streams: StreamQuery, label_generator: Optional[Callable[[Stream], str]] = None) -> List[Stream]:
    """Prompts the user to select one or more of the provided `streams`.

    Args:
        streams:
            A collection of streams the user must choose from.
        label_generator:
            A callback function to allow customization of label generation. By default labels 
            are generated in the following format "stream {stream_itag}".

    Returns:
        A `List` of `Stream` chosen by the user.
    """

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
    picked_streams = cast(List[Stream], [ picked_option[0].value for picked_option in stream_pick_menu ])

    logger.info("picked stream itags %s", list(map(lambda s: s.itag, picked_streams)))

    return picked_streams
