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
that raises anything else is recorded as ``SOLVER_ERROR``. `SolveStatus` lists when a solve is
recorded as ``DIVERGED``; no bound on how far an iterate may stray exists.

This package relies on 2 facts:

- **Orientation.** The framework supports both orientations: the interval's class, `IncreasingInterval`
  or `DecreasingInterval`, says which one an interval has. The benchmark's own function portfolio is
  entirely increasing, ``f(a) < 0 < f(b)``, so a solver may support only that case, and how it
  treats a decreasing interval is its author's choice.
- **Flop counting.** Everything inside `Solver.solve`'s counting context runs on `CountedFloat` and
  is counted: the zero and sign checks on ``f(a)`` and ``f(b)``, ``xtol``, the bookkeeping of the
  best estimate, and the solver's own arithmetic. The validation before the context and the
  divergence checks after it are uncounted, and `WrappedFunction` pauses counting while ``f``
  itself runs, so the function's cost is never included.

The module `stopping` holds `interval_root_if_converged`, which applies the stopping criterion of
`Interval.is_converged` and the root estimate of `Interval.root` to 2 interval bounds, for the solvers that keep
their interval bounds in variables of their own.

A solver class carries only its algorithm. A `SolverConfig` records the init arguments that the benchmark passes
to a solver, and its `SolverRole` decides how the benchmark treats the result; 1 `SolverConfigs` subclass per
solver class declares that solver's configs, and `SolverConfigRegistry` holds every registered config.
"""

from .config import SolverConfig, SolverConfigs
from .interval import DecreasingInterval, IncreasingInterval, Interval, IntervalBound
from .registry import SolverConfigRegistry
from .result import SolveResult, SolveStatus
from .role import SolverRole
from .solver import BracketingSolver, Solver
from .state import SolveState
