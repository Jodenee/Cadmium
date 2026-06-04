from collections import namedtuple
from typing import Literal, NamedTuple, Union

from core.utilities.constants import YOUTUBE_CHANNEL_REGEX, YOUTUBE_PLAYLIST_REGEX, YOUTUBE_VIDEO_REGEX
from ..enums import MediaType

class _UrlParseSuccess(NamedTuple):
    success: Literal[True]
    mediaType: MediaType

class _UrlParseFailure(NamedTuple):
    success: Literal[False]
    mediaType: None

UrlParseResult = Union[_UrlParseSuccess, _UrlParseFailure]

def parse_youtube_link_type(url: str) -> UrlParseResult:
    """Parses a `MediaType` from a youtube url.

    Args:
        url: A url of either a video, playlist or channel.

    Returns:
        A tuple containing a success flag and `MediaType` that represents the type of media the provided url leads to.
    """
    
    if (url.isspace()):
        return _UrlParseFailure(False, None)

    if YOUTUBE_VIDEO_REGEX.match(url):
        return _UrlParseSuccess(True, MediaType.VIDEO)
    elif YOUTUBE_PLAYLIST_REGEX.match(url):
        return _UrlParseSuccess(True, MediaType.PLAYLIST)
    elif YOUTUBE_CHANNEL_REGEX.match(url):
        return _UrlParseSuccess(True, MediaType.CHANNEL)
    else:
        return _UrlParseFailure(False, None)
