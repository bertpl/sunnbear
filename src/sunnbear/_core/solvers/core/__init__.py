"""This package holds the base classes that make any root solver benchmarkable.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. One call to ``solve`` runs
the pieces in this order::

    Solver.solve(f, a, b, xtol=..., max_fevals=...)       [template method]
      │ wraps f in a WrappedFunction, which applies the budget, the guards, the flop
      │   pause, sign normalization, and history to each evaluation
      │ evaluates f(a), f(b); normalizes so that f(a) <= 0 <= f(b)
      │ opens the flop-counting context; a, b become CountedFloat
      ▼
    Solver._solve(run: SolveRun)                           [subclass hook]
      │   BracketingSolver implements it as a loop over _step(run, Interval, state)
      │   with the stopping criteria owned by the base
      ▼
    SolveResult

An abnormal ending is a `SolveInterrupt` exception, raised by the wrapper and
mapped to a `SolveStatus` by `Solver.solve`; a solver that raises anything else
is recorded as ``SOLVER_ERROR``.
"""

from .interval import Interval
from .result import SolveResult, SolveStatus
from .run import SolveRun
from .solver import BracketingSolver, Solver
