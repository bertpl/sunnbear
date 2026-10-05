"""`IllinoisMpmathTwin` runs mpmath's Illinois method as a `Solver`, so `Illinois` can be tested against it.

mpmath implements the Illinois method, the Pegasus method and the Anderson–Björck method as 1 solver class whose
`method` keyword picks the scaling of the retained bound's function value. The twin runs it in mpmath's float64
context, `mpmath.fp`, so its arithmetic is plain float64. A twin exists for agreement tests only: it is never
registered and never benchmarked.

Declared deviations from exact agreement:

- mpmath evaluates both interval bounds again before its first iterate;
- mpmath computes the chord's zero as ``a - fa / ((fb - fa) / (b - a))``, anchored at the retained point, where
  `Illinois` uses regula falsi's ``(a * fb - b * fa) / (fb - fa)``, so the iterates can differ in their last bits.
"""

import mpmath
from mpmath.calculus.optimization import Illinois as MpmathIllinois

from sunnbear.solvers import Solver, SolveState
from tests.solvers.twins import TwinConverged, TwinDeviations, TwinFunction

DEVIATIONS = TwinDeviations(n_reevaluated_bounds=2)


class IllinoisMpmathTwin(Solver):
    """`IllinoisMpmathTwin` runs mpmath's Illinois method on the interval and returns the root where sunnbear stops."""

    name = "illinois_mpmath_twin"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Iterate mpmath's solver through a `TwinFunction`, which stops it where `Illinois` would stop."""
        f = TwinFunction(state, DEVIATIONS.n_reevaluated_bounds)
        interval = [float(state.interval.a), float(state.interval.b)]
        # A tolerance of 0 disables mpmath's own stopping test on |f|, so TwinConverged always ends the loop.
        try:
            for _ in MpmathIllinois(mpmath.fp, f, interval, tol=0.0, verbose=False, method="illinois"):
                pass
        except TwinConverged as converged:
            return converged.x
        raise AssertionError("mpmath's loop ended before sunnbear's stopping criterion held.")
