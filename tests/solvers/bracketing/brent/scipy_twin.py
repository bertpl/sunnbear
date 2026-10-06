"""`BrentScipyTwin` runs `scipy.optimize.brentq` as a `Solver`, so `Brent` can be tested against it."""

import sys

import scipy.optimize

from sunnbear.solvers import Interval
from tests.solvers.twins import StoppingWrappedFunction, TwinSolver

_MACHEPS = sys.float_info.epsilon


class BrentScipyTwin(TwinSolver):
    """`BrentScipyTwin` hands the interval to `scipy.optimize.brentq` and returns ``b`` after the evaluation at which
    `Brent` would stop.

    SciPy's ``brentq`` follows the Fortran version of Brent's procedure on netlib. Its tolerance,
    ``(xtol + rtol * |b|) / 2``, equals Brent's ``tol = 2 * macheps * |b| + t`` with ``t`` the absolute tolerance
    that `Brent` derives from its ``xtol``, when the twin passes brentq ``xtol=2 * t`` and ``rtol=4 * macheps``, so
    SciPy's steps match those of `Brent`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first step;
    - SciPy computes the interpolation step from divided differences, where `Brent` computes it as ``p / q``, so the
      evaluated points can differ in their last bits;
    - SciPy tests a few of Brent's conditions with a strict inequality where Brent's procedure has a non-strict one,
      and the reverse; a strict and a non-strict comparison give different results only when
      the 2 sides are exactly equal.
    """

    name = "brent_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's brentq with ``xtol`` and ``rtol`` set so that its tolerance equals Brent's ``tol``.

        The twin runs 1 solve at a time, so it keeps that solve's ``t`` on the instance for
        `_root_if_sunnbear_solver_stops`.
        """
        self._brent_t = 0.5 * (xtol - 6.0 * _MACHEPS * max(abs(a), abs(b)))
        scipy.optimize.brentq(f, a, b, xtol=2.0 * self._brent_t, rtol=4.0 * _MACHEPS)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``b`` if `Brent` stops after the last of ``evaluations``, or ``None`` if it continues.

        As in `Brent`, ``b`` is the interval bound with the smaller ``|f|``, and the newest point when both are
        equal.
        """
        (b, fb), (c, _) = self._bounds_by_smaller_abs_f(interval, evaluations)
        if abs(0.5 * (c - b)) <= 2.0 * _MACHEPS * abs(b) + self._brent_t or fb == 0.0:
            return b
        else:
            return None
