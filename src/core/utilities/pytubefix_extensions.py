from typing import Callable, Iterable, cast
from pytubefix import AsyncYouTube, StreamQuery, YouTube, Stream

def stream_repr(stream: Stream) -> str:
    """Produces a user friendly description of a stream. 

    Args:
        stream: `Stream` to repr.

    Returns:
        A user friendly description of the stream.
    """

    separator = " | "
    fps = stream.fps if hasattr(stream, 'fps') else 'N/A'
    resolution = stream.resolution if hasattr(stream, 'resolution') and stream.resolution is not None else 'N/A'
    abr = stream.abr if stream.abr is not None else 'N/A'
    video_codec = stream.video_codec if stream.video_codec is not None else 'N/A'
    audio_codec = stream.audio_codec if stream.audio_codec is not None else 'N/A'

    information_text = str.join(separator, (
        f"subtype: {stream.subtype}",
        f"has video track: {stream.includes_video_track}",
        f"has audio track: {stream.includes_audio_track}",
        f"fps: {fps}",                      
        f"resolution: {resolution}",
        f"average bitrate: {abr}",
        f"file size in MB: {stream.filesize_mb}",
        f"video codec: {video_codec}",
        f"audio codec: {audio_codec}"
    ))

    return information_text


def get_youtube_from_stream(stream: Stream) -> YouTube | AsyncYouTube:
    """Retrieves the `YouTube` instance from the given stream.

    Args:
        stream: `Stream` to extract the YouTube instance from.

    Returns:
        `YouTube` or `AsyncYouTube` depending if the async api was used to fetch the stream.
    """

    youtube = stream._monostate.youtube

    if isinstance(youtube, YouTube):
        return cast(YouTube, youtube)
    else: 
        return cast(AsyncYouTube, youtube)

def get_highest_resolution(streams: StreamQuery, whitelisted_resolutions: Iterable[str] | None = None) -> Stream | None:
    custom_filters: list[Callable[[Stream], bool]] = []

    if whitelisted_resolutions is not None:
        custom_filters.append(
            lambda s: s.resolution in whitelisted_resolutions
        )

    filtered_streams = streams.filter(
        is_dash=True, 
        only_video=True,
        custom_filter_functions=custom_filters
    )

    try:
        return sorted(
            filtered_streams, 
            key=lambda s: int(s.resolution.removesuffix("p")), # type: ignore
            reverse=True
        )[0]
    except IndexError:
        return None

def get_highest_average_bitrate(streams: StreamQuery, whitelisted_average_bitrates: Iterable[str] | None = None) -> Stream | None:
    custom_filters: list[Callable[[Stream], bool]] = []

    if whitelisted_average_bitrates is not None:
        custom_filters.append(
            lambda s: s.abr in whitelisted_average_bitrates
        )

    filtered_streams = streams.filter(
        is_dash=True, 
        only_audio=True,
        custom_filter_functions=custom_filters
    )

    try:
        return sorted(
            filtered_streams, 
            key=lambda s: int(s.abr.removesuffix("kbps")), # type: ignore
            reverse=True
        )[0]
    except IndexError:
        return None