from typing import NamedTuple, Literal

class ReturnResultSuccess[T](NamedTuple):
    success: Literal[True]
    value: T

class ReturnResultFailure(NamedTuple):
    success: Literal[False]
    message: str

type ReturnResult[T] = ReturnResultSuccess[T] | ReturnResultFailure