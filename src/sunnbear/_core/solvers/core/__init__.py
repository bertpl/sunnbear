"""This package implements the framework and fundamental building blocks used to implement solvers for benchmarking.

A solver receives a plain ``f(x) -> float`` and a bracketing interval ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. One call to ``solve`` runs
the pieces in this order::

    Solver.solve(f, a, b, xtol=..., max_fevals=...)       [template method]
      │ wraps f in a WrappedFunction, which runs the per-evaluation checks documented on that class
      │ evaluates f(a), f(b); Interval.from_interval_bounds picks the interval's orientation from them
      │ opens the flop-counting context; a, b become CountedFloat
      ▼
    Solver._solve(state: SolveState)                      [subclass hook]
      │   BracketingSolver implements it as a loop of _next_x(state, Interval) calls; see that
      │   class for what each iteration does
      ▼
    SolveResult

An abnormal ending is a `SolveException` (see that class); a solver
that raises anything else is recorded as ``SOLVER_ERROR``. A solve whose result, or whose
function error, lies outside ``[a, b]`` is recorded as ``DIVERGED``; no bound on how far an
iterate may stray exists.

Two facts hold throughout this package:

- **Orientation.** The framework supports both orientations: the interval's class, `IncreasingInterval`
  or `DecreasingInterval`, says which one an interval has. The benchmark's own function portfolio is
  entirely increasing, ``f(a) < 0 < f(b)``, so a solver may support only that case, and how it
  treats a decreasing interval is its author's choice.
- **Flop counting.** Everything inside `Solver.solve`'s counting context runs on `CountedFloat` and
  is counted: the zero and sign checks on ``f(a)`` and ``f(b)``, ``xtol``, the bookkeeping of the
  best estimate, and the solver's own arithmetic. The validation before the context and the
  divergence checks after it are uncounted, and `WrappedFunction` pauses counting while ``f``
  itself runs, so the function's cost is never included.

A solver class carries only its algorithm. A `SolverConfig` records which init arguments the benchmark runs a
solver with, and its `SolverRole` decides how the benchmark treats the result; `SolverConfigRegistry` holds
every registered config.
"""

from .config import SolverConfig
from .interval import DecreasingInterval, IncreasingInterval, Interval, IntervalBound
from .registry import SolverConfigRegistry
from .result import SolveResult, SolveStatus
from .role import SolverRole
from .solver import BracketingSolver, Solver
from .state import SolveState
