"""This module re-exports the solver base classes and the classes that a solver subclass works with.

How a solve runs is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolverState` and never constructs one.
"""

from ._core.solvers.core import (
    BracketingSolver,
    DecreasingInterval,
    IncreasingInterval,
    Interval,
    Solver,
    SolveResult,
    SolverState,
    SolveStatus,
)

__all__ = [
    "BracketingSolver",
    "DecreasingInterval",
    "IncreasingInterval",
    "Interval",
    "SolveResult",
    "SolveStatus",
    "Solver",
    "SolverState",
]
