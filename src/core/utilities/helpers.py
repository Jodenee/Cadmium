# Generics

from re import sub as re_sub

from .constants import MATCH_CONSECUTIVE_SPACES

# Helper functions

def choose[K, T](key: K, map: dict[K, T], default: T) -> T:
    """Chooses a value from a dictionary using a provided key.

    Args:
        key: Key to access the map
        map: Map containing various keys and values
        default: the default key to use in case of a `KeyError`.

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
        text: the text to modify.

    Returns:
        The text with collapsed whitespace 

    Examples:
        >>> collapse_whitespace("Hello,  World!")
        "Hello, World!"
    """

    return re_sub(MATCH_CONSECUTIVE_SPACES, " ", text)
