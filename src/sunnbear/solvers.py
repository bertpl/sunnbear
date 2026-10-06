"""This module re-exports the solver base classes, the interval, state, config, and registry classes, and the solvers.

How a solve runs is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolveState` and never constructs one.
Importing this module registers the built-in solver configs with `SolverConfigRegistry`.
"""

from ._core.solvers.bracketing import Bisection, Illinois, RegulaFalsi, Ridders
from ._core.solvers.core import (
    BracketingSolver,
    DecreasingInterval,
    IncreasingInterval,
    Interval,
    IntervalBound,
    Solver,
    SolverConfig,
    SolverConfigRegistry,
    SolveResult,
    SolverRole,
    SolveState,
    SolveStatus,
)

__all__ = [
    "Bisection",
    "BracketingSolver",
    "DecreasingInterval",
    "Illinois",
    "IncreasingInterval",
    "Interval",
    "IntervalBound",
    "RegulaFalsi",
    "Ridders",
    "SolveResult",
    "SolveState",
    "SolveStatus",
    "Solver",
    "SolverConfig",
    "SolverConfigRegistry",
    "SolverRole",
]
