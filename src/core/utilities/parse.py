from core.utilities.constants import YOUTUBE_CHANNEL_REGEX, YOUTUBE_PLAYLIST_REGEX, YOUTUBE_VIDEO_REGEX
from ..enums import MediaType
from ..exceptions import InvalidYoutubeURLError


def parse_youtube_link_type(url: str) -> MediaType:
    """Parses a `MediaType` from a youtube url.

    Args:
        url: A url of either a video, playlist or channel.

    Returns:
        A `MediaType` that represents the type of media the provided url leads to.

    Raises:
        InvalidYoutubeURLError: 
            Raised if `url` is not a valid youtube url leading to either a video, playlist or channel.
    """
    
    if (url.isspace()):
        raise InvalidYoutubeURLError(url)

    if YOUTUBE_VIDEO_REGEX.match(url):
        return MediaType.VIDEO
    elif YOUTUBE_PLAYLIST_REGEX.match(url):
        return MediaType.PLAYLIST
    elif YOUTUBE_CHANNEL_REGEX.match(url):
        return MediaType.CHANNEL
    else:
        raise InvalidYoutubeURLError(url)
