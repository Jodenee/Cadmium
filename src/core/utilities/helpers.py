# Generics

from re import sub as re_sub
from typing import Dict, TypeVar

# Generic variables

K = TypeVar("K")
T = TypeVar("T")

# Helper functions

def choose(key: K, map: Dict[K, T], default: T) -> T:
    try:
        return map[key]
    except KeyError:
        return default
    
    
def collapse_whitespace(text: str) -> str:
    return re_sub(r"\s+", " ", text)
