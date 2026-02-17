# Generics

from re import sub as re_sub
from typing import Dict, TypeVar

from core.utilities.constants import MATCH_CONSECUTIVE_SPACES

# Generic variables

K = TypeVar("K")
T = TypeVar("T")

# Helper functions

def choose(key: K, map: Dict[K, T], default: T) -> T:
    """Chooses a value from a dictionary using a provided key.

    Args:
        key: An optional Path to the ffmpeg executable to be used.
        map: The file extension to be converted to.
        default: the file extension configuration name.

    Returns:
        A value from the dictionary, if the key does not exist the default value is returned.
    """

    try:
        return map[key]
    except KeyError:
        return default
    
    
def collapse_whitespace(text: str) -> str:
    """Collapses whitespace in the provided text.

    Args:
        text: A `string`.

    Returns:
        A string with collapsed whitespace 

    Examples:
        >>> collapse_whitespace("Hello,  World!")
        "Hello, World!"
    """

    return re_sub(MATCH_CONSECUTIVE_SPACES, " ", text)
