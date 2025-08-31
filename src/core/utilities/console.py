from typing import Generic, Optional, Tuple, TypeVar

def spaced_print(*objects, sep: Optional[str] = "", flush: bool = False, end: Optional[str] = None) -> None:
    print(*("\n", *objects), sep=sep, flush=flush, end=end)
