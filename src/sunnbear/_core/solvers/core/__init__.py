"""This package implements the framework and fundamental building blocks used to implement solvers for benchmarking.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows nothing of test
functions or the benchmark that drives the solver.

`WrappedFunction` is a solver's only way to evaluate ``f``: it applies an evaluation budget, a
guard against evaluations too far outside the bracket, and a check that each value is finite, and
raises a `SolveInterrupt` when the solve must stop early.

`Interval` is a bracketing solver's bracket, and `SolveRun` is the mutable state of one solve.
"""

from .interval import Interval
from .run import SolveRun
