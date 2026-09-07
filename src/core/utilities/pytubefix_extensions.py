from typing import cast
from pytubefix import AsyncYouTube, YouTube, Stream

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
    bitrate = f"{stream.bitrate / 1000}kbps" if stream.bitrate is not None else 'N/A'
    video_codec = stream.video_codec if stream.video_codec is not None else 'N/A'
    audio_codec = stream.audio_codec if stream.audio_codec is not None else 'N/A'

    information_text = str.join(separator, (
        f"subtype: {stream.subtype}",
        f"has video track: {stream.includes_video_track}",
        f"has audio track: {stream.includes_audio_track}",
        f"fps: {fps}",                      
        f"resolution: {resolution}",
        f"bitrate: {bitrate}",
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
