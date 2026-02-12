# Generics

import re
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
