"""This module re-exports the solver base classes and the types in `Solver.solve`'s signature.

How a solve runs is described in the docstring of the implementation package, `sunnbear._core.solvers.core`.
`WrappedFunction` is deliberately absent: a solver receives one inside its `SolverState` and never constructs one.
"""

from ._core.solvers.core import BracketingSolver, Interval, Solver, SolveResult, SolverState, SolveStatus

__all__ = ["BracketingSolver", "Interval", "SolveResult", "SolveStatus", "Solver", "SolverState"]
