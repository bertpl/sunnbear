"""This package holds the pieces a solve is built from: the bracket, the wrapped function, and the per-solve run.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows
nothing of test functions or the benchmark that drives it. `WrappedFunction` is
the only route through which a solver evaluates ``f``: it applies the budget and
the guards to each evaluation and raises a `SolveInterrupt` when the solve must
stop early. `Interval` is the bracket a bracketing solver reduces, and `SolveRun`
is the mutable state of one solve.
"""

from .interval import Interval
from .run import SolveRun
