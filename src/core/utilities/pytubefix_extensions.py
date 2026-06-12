from typing import cast
from pytubefix import AsyncYouTube, YouTube, Stream

def stream_repr(stream: Stream) -> str:
    """Produces a user friendly description of a stream. 

    Args:
        stream: A `Stream`.

    Returns:
        A user friendly description of the stream.
    """

    separator = " | "
    fps = stream.fps if hasattr(stream, 'fps') else 'N/A'
    bitrate = f"{stream.bitrate / 1000}kbps" if stream.bitrate != None else 'N/A'

    information_text = str.join(separator, (
        f"subtype: {stream.subtype}",
        f"has video track: {stream.includes_video_track}",
        f"has audio track: {stream.includes_audio_track}",
        f"fps: {fps}",                                    
        f"resolution: {stream.resolution}",              
        f"bitrate: {bitrate}",              
        f"file size (MB): {stream.filesize_mb}",
        f"video codec: {stream.video_codec}",
        f"audio codec: {stream.audio_codec}"
    ))

    return information_text


def get_youtube_from_stream(stream: Stream) -> YouTube | AsyncYouTube:
    youtube = stream._monostate.youtube

    if isinstance(youtube, YouTube):
        return cast(YouTube, youtube)
    else: 
        return cast(AsyncYouTube, youtube)
