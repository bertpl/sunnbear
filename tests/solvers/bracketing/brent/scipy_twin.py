"""`BrentScipyTwin` runs `scipy.optimize.brentq` or `scipy.optimize.brenth` as a `Solver`, so `Brent` can be tested
against them."""

import scipy.optimize

from sunnbear._core.utils.floats import FLOAT64_EPS
from sunnbear.solvers import BrentVariant
from tests.solvers.twins import StoppingWrappedFunction, TwinSolver

# Each variant maps to the function of SciPy that implements its method.
_SCIPY_FUNCTIONS = {
    BrentVariant.HYPERBOLIC: scipy.optimize.brenth,
    BrentVariant.INVERSE_QUADRATIC: scipy.optimize.brentq,
}


class BrentScipyTwin(TwinSolver):
    """`BrentScipyTwin` hands the interval to the function of SciPy that implements the twin's variant, and stops it
    where `Brent` stops, by the shared stopping criterion of `TwinSolver`.

    SciPy's ``brentq`` is SciPy's own C implementation of Brent's method, the method of ``"inverse_quadratic"``.
    SciPy's ``brenth``, the method of ``"hyperbolic"``, is ``brentq`` with hyperbolic interpolation in place of inverse
    quadratic interpolation. Their tolerance, ``(xtol + rtol*|b|) / 2``, equals Brent's ``tol = 2*macheps*|b| + t``
    with ``t = xtol``, as `Brent` sets it, when the twin passes SciPy ``xtol=2*xtol`` and ``rtol=4*macheps``, so SciPy's
    steps match those of `Brent`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first step;
    - SciPy computes the secant step, and the inverse quadratic step of ``brentq``, in forms of its own, where `Brent`
      computes them as ``p / q`` in the forms of Brent's procedure, so the evaluated x-values can differ in their last
      bits; `Brent` computes the hyperbolic step of ``brenth`` in SciPy's form;
    - where the product in the denominator of the inverse quadratic step of ``brentq`` underflows to 0, as on ``x^19``
      near its root, SciPy bisects where `Brent` interpolates; no twin test case reaches such a bisection;
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

    def __init__(self, *, variant: BrentVariant) -> None:
        """Take the variant of the twin's `Brent` config."""
        self.variant = variant

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run the function of SciPy for the variant, with ``xtol`` and ``rtol`` set so that its tolerance equals
        Brent's ``tol``."""
        _SCIPY_FUNCTIONS[self.variant](f, a, b, xtol=2.0 * xtol, rtol=4.0 * FLOAT64_EPS)
