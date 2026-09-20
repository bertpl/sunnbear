"""This module re-exports the base classes that a benchmarkable solver subclasses, and the types `Solver.solve` uses.

How a solve runs is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolveRun` and never constructs one.
"""

from ._core.solvers.core import BracketingSolver, Interval, Solver, SolveResult, SolveRun, SolveStatus

__all__ = ["BracketingSolver", "Interval", "SolveResult", "SolveRun", "SolveStatus", "Solver"]
