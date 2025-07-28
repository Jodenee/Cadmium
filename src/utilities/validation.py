
from re import compile as compile_regex
from enums import MediaType
from exceptions import InvalidYoutubeURLError

youtube_regex = compile_regex(
    r'^((?:https?:)?//)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu\.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$'
)

def parse_youtube_link_type(url: str) -> MediaType:
    if (url.isspace()):
        raise InvalidYoutubeURLError(url)
    
    match = youtube_regex.match(url)

    if (match == None):
        raise InvalidYoutubeURLError(url)
    
    return MediaType.PLAYLIST if match.group(5) == "playlist" else MediaType.VIDEO