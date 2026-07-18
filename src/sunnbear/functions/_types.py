"""Callable type aliases for test functions.

Kept in their own module so both the formula layer and the materialized
test-function layer can import them without depending on each other.
"""

from collections.abc import Callable

# Hot signature of a materialized formula: f(x, c) -> float, 64-bit in and out.
XCFun = Callable[[float, float], float]

# Single-argument view of a test function once c is bound: f(x) -> float.
XFun = Callable[[float], float]
