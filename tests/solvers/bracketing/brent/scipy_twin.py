"""`BrentScipyTwin` runs `scipy.optimize.brentq` as a `Solver`, so `Brent` can be tested against it."""

import scipy.optimize

from sunnbear._core.utils.floats import FLOAT64_EPS
from tests.solvers.twins import StoppingWrappedFunction, TwinSolver


class BrentScipyTwin(TwinSolver):
    """`BrentScipyTwin` hands the interval to `scipy.optimize.brentq`, and stops it where `Brent` stops, by the shared
    stopping criterion of `TwinSolver`.

    SciPy's ``brentq`` is SciPy's own C implementation of Brent's method. Its tolerance, ``(xtol + rtol*|b|) / 2``,
    equals Brent's ``tol = 2*macheps*|b| + t`` with ``t = xtol``, as `Brent` sets it, when the twin passes brentq
    ``xtol=2*xtol`` and ``rtol=4*macheps``, so SciPy's steps match those of `Brent`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first step;
    - SciPy computes the interpolation step from divided differences, where `Brent` computes it as ``p / q``, so the
      evaluated x-values can differ in their last bits; where the product in the denominator of SciPy's inverse
      quadratic step underflows to 0, as on ``x^19`` near its root, SciPy bisects where `Brent` interpolates; no twin
      test case reaches such a bisection;
    - SciPy tests a few of Brent's conditions with a strict inequality where Brent's procedure has a non-strict one,
      and the reverse; a strict and a non-strict comparison give different results only when
      the 2 sides are exactly equal;
    - SciPy accepts an interpolation step by comparing step lengths only, without Brent's test of the step's
      direction toward ``c``; no twin test case reaches a step on which the 2 tests differ;
    - SciPy stops by its own criterion once the interval is narrower than ``2*tol``, which can happen before it is
      ``2*xtol`` wide; `TwinSolver` then fails the comparison, and no twin test case reaches such a stop.
    """

    name = "brent_scipy_twin"
    version = 2
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's brentq with ``xtol`` and ``rtol`` set so that its tolerance equals Brent's ``tol``."""
        scipy.optimize.brentq(f, a, b, xtol=2.0 * xtol, rtol=4.0 * FLOAT64_EPS)
