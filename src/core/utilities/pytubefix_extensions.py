from pytubefix import YouTube, Stream, Channel

def stream_repr(stream: Stream) -> str:
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
    

# Temporary fix for channel video_urls generator returning YoutubeVideo instances (https://github.com/JuanBindez/pytubefix/issues/577)
def get_channel_video_urls(channel: Channel):
    video: YouTube
    for video in channel.video_urls:
        yield video.watch_url
