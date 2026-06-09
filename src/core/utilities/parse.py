import logging

from typing import Literal, NamedTuple, Union

from core.utilities.constants import YOUTUBE_CHANNEL_REGEX, YOUTUBE_PLAYLIST_REGEX, YOUTUBE_VIDEO_REGEX, APPLICATION_LOGGER_NAME
from ..enums import MediaType

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

# Types

class _UrlParseSuccess(NamedTuple):
    success: Literal[True]
    mediaType: MediaType

class _UrlParseFailure(NamedTuple):
    success: Literal[False]
    mediaType: None

UrlParseResult = Union[_UrlParseSuccess, _UrlParseFailure]

# Functions

def parse_youtube_link_type(url: str) -> UrlParseResult:
    """Parses a `MediaType` from a youtube url.

    Args:
        url: A url of either a video, playlist or channel.

    Returns:
        A tuple containing a success flag and `MediaType` that represents the type of media the provided url leads to.
    """
    
    parse_result: UrlParseResult

    if (url.isspace()):
        logging.debug("could not parse empty string into a valid media type")
        parse_result = _UrlParseFailure(False, None)
    elif YOUTUBE_VIDEO_REGEX.match(url):
        parse_result = _UrlParseSuccess(True, MediaType.VIDEO)
    elif YOUTUBE_PLAYLIST_REGEX.match(url):
        parse_result = _UrlParseSuccess(True, MediaType.PLAYLIST)
    elif YOUTUBE_CHANNEL_REGEX.match(url):
        parse_result = _UrlParseSuccess(True, MediaType.CHANNEL)
    else:
        logging.debug("url=%s could not be parsed into a known MediaType", url)
        parse_result = _UrlParseFailure(False, None)

    if parse_result.success is True:
        logger.info("%r successfully parsed as %s", url, parse_result.mediaType.name)
    
    return parse_result
