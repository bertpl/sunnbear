"""This package holds the base classes that make any root solver benchmarkable.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. One call to ``solve`` runs
the pieces in this order::

    Solver.solve(f, a, b, xtol=..., max_fevals=...)       [template method]
      │ wraps f in a WrappedFunction, which runs the per-evaluation checks documented on that class
      │ evaluates f(a), f(b); normalizes so that f(a) <= 0 <= f(b)
      │ opens the flop-counting context; a, b become CountedFloat
      ▼
    Solver._solve(run: SolveRun)                           [subclass hook]
      │   BracketingSolver implements it as a loop over _step(run, Interval, state)
      │   with the stopping criteria owned by BracketingSolver
      ▼
    SolveResult

An abnormal ending is a `SolveInterrupt` exception (see that class); a solver
that raises anything else is recorded as ``SOLVER_ERROR``.
"""

from .interval import Interval
from .result import SolveResult, SolveStatus
from .run import SolveRun
from .solver import BracketingSolver, Solver
