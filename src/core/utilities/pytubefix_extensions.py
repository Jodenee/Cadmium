from typing import Union, cast

from pytubefix import YouTube, Stream, Channel

def stream_repr(stream: Stream) -> str:
    return f"subtype: {stream.subtype}, fps: {stream.fps if hasattr(stream, 'fps') else '0'}, resolution: {stream.resolution}, bitrate: {stream.bitrate / 1000 if stream.bitrate != None else '?'}kbps, file size (MB): {stream.filesize_mb}, includes video track: {stream.includes_video_track}, includes audio track: {stream.includes_audio_track}, video codec: {stream.video_codec}, audio codec: {stream.audio_codec}"

# Temporary fix for channel video_urls generator returning YoutubeVideo instances
def get_channel_video_urls(channel: Channel):
    video: YouTube
    for video in channel.video_urls:
        yield video.watch_url
