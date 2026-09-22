"""This module re-exports the solver base classes, the interval and state classes, and the shipped solvers.

How a solve runs is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolveState` and never constructs one.
"""

from ._core.solvers.bracketing import Bisection, RegulaFalsi
from ._core.solvers.core import (
    BracketingSolver,
    DecreasingInterval,
    IncreasingInterval,
    Interval,
    IntervalBound,
    Solver,
    SolveResult,
    SolveState,
    SolveStatus,
)

__all__ = [
    "Bisection",
    "BracketingSolver",
    "DecreasingInterval",
    "IncreasingInterval",
    "Interval",
    "IntervalBound",
    "RegulaFalsi",
    "SolveResult",
    "SolveState",
    "SolveStatus",
    "Solver",
]
