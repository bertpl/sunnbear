"""`BrentScipyTwin` runs `scipy.optimize.brentq` as a `Solver`, so `Brent` can be tested against it."""

import sys

import scipy.optimize

from sunnbear.solvers import Interval
from tests.solvers.twins import TwinFunction, TwinSolver

_MACHEPS = sys.float_info.epsilon


class BrentScipyTwin(TwinSolver):
    """`BrentScipyTwin` hands the interval to `scipy.optimize.brentq` and returns ``b`` at the point where `Brent`
    would stop.

    SciPy's ``brentq`` follows netlib's ``zeroin.f``, the Fortran version of Brent's procedure. Its tolerance,
    ``(xtol + rtol * |b|) / 2``, equals Brent's ``tol = 2 * macheps * |b| + t`` when the twin passes ``xtol = 2 * t``
    and ``rtol = 4 * macheps``, so its steps match those of `Brent`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first step;
    - SciPy computes the interpolation step from divided differences, where `Brent` computes it as ``p / q``, so the
      evaluated points can differ in their last bits;
    - SciPy tests a few of Brent's conditions with a strict inequality where Brent's procedure has a non-strict one,
      and the reverse; the 2 differ only when the 2 sides are exactly equal.
    """

    name = "brent_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's brentq with the tolerances that make its tolerance equal Brent's ``tol``.

        The twin runs 1 solve at a time, so it keeps that solve's ``t`` on the instance for
        `_root_if_sunnbear_solver_stops`.
        """
        self._t = 0.5 * (xtol - 6.0 * _MACHEPS * max(abs(a), abs(b)))
        scipy.optimize.brentq(f, a, b, xtol=2.0 * self._t, rtol=4.0 * _MACHEPS)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``b`` if `Brent` stops after the last of ``evaluations``, or ``None`` if it continues.

        As in `Brent`, ``b`` is the interval bound with the smaller ``|f|``, the newest point when both are equal,
        and `Brent` stops once half the interval is at most ``2 * macheps * |b| + t``, or ``f(b)`` is 0.
        """
        x_newest, f_newest = evaluations[-1]
        if x_newest == interval.a:
            x_other, f_other = interval.b, interval.fb
        else:
            x_other, f_other = interval.a, interval.fa
        if abs(f_other) < abs(f_newest):
            b, fb, c = x_other, f_other, x_newest
        else:
            b, fb, c = x_newest, f_newest, x_other
        if abs(0.5 * (c - b)) <= 2.0 * _MACHEPS * abs(b) + self._t or fb == 0.0:
            return b
        else:
            return None
