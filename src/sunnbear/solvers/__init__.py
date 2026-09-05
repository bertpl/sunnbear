"""Solver framework: the base classes a benchmarkable solver subclasses, and the reference solvers.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. How the pieces tie
together in one call to ``solve``::

    Solver.solve(f, a, b, xtol=..., max_fevals=...)       [template method]
      │ wraps f in a WrappedFunction: evaluation count + budget, divergence and
      │   domain guards, flop pause around f, sign normalization, history
      │ evaluates f(a), f(b); normalizes so that f(a) <= 0 <= f(b)
      │ opens the flop-counting context; a, b become CountedFloat
      ▼
    Solver._solve(run: SolveRun)                           [subclass hook]
      │   BracketingSolver implements it as a loop over _step(run, Interval, state)
      │   with the stopping criteria owned by the base
      ▼
    SolveResult ── x · SolveStatus · n_fevals · n_iters · FlopCounts · history

Abnormal endings travel as `SolveInterrupt` exceptions (see `sunnbear.errors`)
raised by the wrapper and mapped to a `SolveStatus` by the template method; a
solver that raises anything else is recorded as ``SOLVER_ERROR``.
"""

from ._bisection import Bisection
from ._interval import Interval
from ._result import SolveResult, SolveStatus
from ._run import SolveRun
from ._solver import BracketingSolver, Solver
