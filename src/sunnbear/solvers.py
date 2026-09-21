"""This module re-exports the classes that a solver implementation works with.

What each one is for is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolverState` and never constructs one.
"""

from ._core.solvers.core import DecreasingInterval, IncreasingInterval, Interval, SolverState

__all__ = ["DecreasingInterval", "IncreasingInterval", "Interval", "SolverState"]
