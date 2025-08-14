from typing import Generic, Optional, Tuple, TypeVar

def spaced_print(*objects, sep: Optional[str] = None, flush: bool = False) -> None:
    print(*objects, end="\n\n", sep=sep, flush=flush)
