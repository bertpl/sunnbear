"""This module defines the callable type aliases for the functions of test problems.

The aliases live in their own module, so that both the `formula` module and the `test_problem` module can import
them without depending on each other.
"""

from collections.abc import Callable

# Hot signature of a materialized formula: f(x, c) -> float, 64-bit in and out.
XCFun = Callable[[float, float], float]

# `XFun` is the single-argument form of a test problem's function once c is bound: f(x) -> float.
XFun = Callable[[float], float]
