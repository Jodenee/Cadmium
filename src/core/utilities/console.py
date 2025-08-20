from typing import Generic, Optional, Tuple, TypeVar

def spaced_print(*objects, sep: Optional[str] = None, flush: bool = False) -> None:
    print(*("\n", *objects), sep=sep, flush=flush)
