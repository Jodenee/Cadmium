from typing import Union, cast

from pytubefix import YouTube, Stream
from pytubefix.async_youtube import AsyncYouTube

# Temporary fix for https://github.com/JuanBindez/pytubefix/issues/529
async def stream_default_filename(stream: Stream) -> str:
    stream_youtube: Union[YouTube, AsyncYouTube] = cast(Union[YouTube, AsyncYouTube], stream._monostate.youtube)
    youtube_title = await stream_youtube.title() if isinstance(stream_youtube, AsyncYouTube) else stream_youtube.title

    return f"{youtube_title}.{stream.subtype}"

def stream_repr(stream: Stream) -> str:
    return f"subtype: {stream.subtype}, fps: {stream.fps if hasattr(stream, 'fps') else '0'}, resolution: {stream.resolution}, bitrate: {stream.bitrate / 1000 if stream.bitrate != None else '?'}kbps, file size (MB): {stream.filesize_mb}, includes video track: {stream.includes_video_track}, includes audio track: {stream.includes_audio_track}, video codec: {stream.video_codec}, audio codec: {stream.audio_codec}"
