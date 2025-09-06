
from re import compile as compile_regex
from ..enums import MediaType
from ..exceptions import InvalidYoutubeURLError

youtube_video_regex = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/(?:watch\?v=|shorts\/)[\w\-]{11}(?:[&\?]\S*)?$")
youtube_playlist_regex = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=[\w\-]+$")
youtube_channel_regex = compile_regex(r"^https?:\/\/(?:www\.)?youtube\.com\/@[\w\-\.]+$")

def parse_youtube_link_type(url: str) -> MediaType:
    if (url.isspace()):
        raise InvalidYoutubeURLError(url)

    if youtube_video_regex.match(url):
        return MediaType.VIDEO
    elif youtube_playlist_regex.match(url):
        return MediaType.PLAYLIST
    elif youtube_channel_regex.match(url):
        return MediaType.CHANNEL
    else:
        raise InvalidYoutubeURLError(url)
