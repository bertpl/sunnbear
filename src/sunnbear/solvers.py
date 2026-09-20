"""This module re-exports the types that a solver implementation works with.

What each one is for is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolveRun` and never constructs one.
"""

from ._core.solvers.core import Interval, SolveRun

__all__ = ["Interval", "SolveRun"]
