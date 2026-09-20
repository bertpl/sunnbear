"""This package implements the framework and fundamental building blocks used to implement solvers for benchmarking.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows nothing of test
functions or the benchmark that drives the solver.

`WrappedFunction` is a solver's only way to evaluate ``f``: it applies an evaluation budget, a
guard against evaluations too far outside the bracket, and a check that each value is finite, raises
a `SolveInterrupt` when the solve must stop early, and records the evaluations when asked.

`Interval` is a bracketing solver's bracket, and `SolverState` is the mutable state of one solve,
which a solver extends with its own fields.
"""

from .interval import Interval
from .state import SolverState
