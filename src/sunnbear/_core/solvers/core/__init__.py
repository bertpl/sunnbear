"""This package implements the framework and fundamental building blocks used to implement solvers for benchmarking.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. One call to ``solve`` runs
the pieces in this order::

    Solver.solve(f, a, b, xtol=..., max_fevals=...)       [template method]
      │ wraps f in a WrappedFunction, which runs the per-evaluation checks documented on that class
      │ evaluates f(a), f(b); requires f(a) < 0 < f(b)
      │ opens the flop-counting context; a, b become CountedFloat
      ▼
    Solver._solve(state: SolverState)                      [subclass hook]
      │   BracketingSolver implements it as a loop over _step(state, Interval)
      │   with the stopping criterion owned by BracketingSolver
      ▼
    SolveResult

An abnormal ending is a `SolveInterrupt` exception (see that class); a solver
that raises anything else is recorded as ``SOLVER_ERROR``.

Two facts hold throughout this package:

- **Orientation.** Every solver may assume ``f(a) < 0 < f(b)``; `Solver.solve` rejects any other
  bracket with a `ValueError`, and nothing normalizes the sign. The restriction is easy for a caller
  to satisfy, and this is a research package in which a solver restricted to that case is acceptable.
- **Flop counting.** `Solver.solve` converts ``a``, ``b``, ``f(a)`` and ``f(b)`` to `CountedFloat`
  before handing them to the solver, so the solver's arithmetic on them is counted; `WrappedFunction`
  pauses counting while ``f`` itself runs.
"""

from .interval import Interval
from .result import SolveResult, SolveStatus
from .solver import BracketingSolver, Solver
from .state import SolverState
