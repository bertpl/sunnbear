"""This package holds the parts that a solve uses: the bracket, the wrapped function, and the per-solve run.

A solver receives a plain ``f(x) -> float`` and a bracket ``[a, b]``; it knows nothing of test
functions or the benchmark that drives it.

`WrappedFunction` is the only way that a solver evaluates ``f``: it applies an evaluation budget and
the divergence and domain guards to each evaluation, and raises a `SolveInterrupt` when the solve
must stop early.

`Interval` is the bracket that a bracketing solver reduces, and `SolveRun` is the mutable state of
one solve.
"""

from .interval import Interval
from .run import SolveRun
