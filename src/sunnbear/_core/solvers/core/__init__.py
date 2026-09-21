"""This package implements the framework and fundamental building blocks used to implement solvers for benchmarking.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows nothing of test
functions or the benchmark that drives the solver.

`WrappedFunction` is a solver's only way to evaluate ``f``. Each call:

- performs checks and raises a `SolveException` subclass accordingly:
  - `MaxFevalsExceeded` when the call would exceed the evaluation budget;
  - `DivergedError` when ``x`` is not finite;
  - `FunctionDomainError` when ``f`` raises or returns a non-finite value;
- shields the evaluation of ``f`` from flop counting (the counted-float package), so only the
  solver's own arithmetic is counted;
- records the evaluation when history recording is on.

`Interval` is a bracketing solver's bracket, and `SolverState` is the mutable state of one solve,
which a solver extends with its own fields.

Two facts hold throughout this package:

- **Orientation.** Every solver may assume ``f(a) < 0 < f(b)``; `Solver.solve` rejects any other
  bracket with a `ValueError`, and nothing normalizes the sign. The restriction is easy for a caller
  to satisfy, and this package is targeted at research settings, to evaluate solver prototypes, where
  this limitation is acceptable.
- **Flop counting.** `Solver.solve` converts ``a``, ``b``, ``f(a)`` and ``f(b)`` to `CountedFloat`
  before handing them to the solver, so the solver's arithmetic on them is counted; `WrappedFunction`
  pauses counting while ``f`` itself runs.
"""

from .interval import Interval
from .state import SolverState
