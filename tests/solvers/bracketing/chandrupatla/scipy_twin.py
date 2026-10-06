"""`ChandrupatlaScipyTwin` runs `scipy.optimize.elementwise.find_root` as a `Solver`, so `Chandrupatla` can be tested
against it."""

import numpy as np
import scipy.optimize.elementwise

from sunnbear.solvers import Interval
from tests.solvers.twins import TwinFunction, TwinSolver


class ChandrupatlaScipyTwin(TwinSolver):
    """`ChandrupatlaScipyTwin` hands the interval to `scipy.optimize.elementwise.find_root`, which implements
    Chandrupatla's method, and returns ``xm``, the interval bound with the smaller ``|f|``, after the evaluation at
    which `Chandrupatla` would stop.

    SciPy stops once the interval is narrower than ``xatol + xrtol * |xm|``, or once ``|f(xm)|`` is at most its
    function tolerances. The twin passes ``xatol = xtol`` and 0 for the other 3 tolerances, which makes SciPy stop
    where `Chandrupatla` stops and keep each new point as far inside the interval as `Chandrupatla` does.

    SciPy calls the function with arrays; the twin evaluates each element through the `TwinFunction`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first point;
    - SciPy computes the interpolated ``t`` with the paper's equation 3, while `Chandrupatla` computes it from the 4
      quotients of the BASIC listing, so the evaluated points can differ in their last bits.
    """

    name = "chandrupatla_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's find_root with ``xtol`` as its only nonzero tolerance."""
        # otypes spares np.vectorize the extra call that it would otherwise make to find the output type.
        tolerances = {"xatol": xtol, "xrtol": 0.0, "fatol": 0.0, "frtol": 0.0}
        scipy.optimize.elementwise.find_root(np.vectorize(f, otypes=[float]), (a, b), tolerances=tolerances)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``xm`` if `Chandrupatla` stops after the last of ``evaluations``, or ``None`` if it continues.

        As in `Chandrupatla`, ``xm`` is the interval bound with the smaller ``|f|``, and the newest point when both
        are equal.
        """
        (xm, fm), (x_other, _) = self._bounds_by_smaller_abs_f(interval, evaluations)
        if 0.5 * xtol / abs(x_other - xm) > 0.5 or fm == 0.0:
            return xm
        else:
            return None
