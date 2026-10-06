"""`ChandrupatlaScipyTwin` runs `scipy.optimize.elementwise.find_root` as a `Solver`, so `Chandrupatla` can be tested
against it."""

import numpy as np
import scipy.optimize.elementwise

from sunnbear.solvers import Interval
from tests.solvers.twins import TwinFunction, TwinSolver


class ChandrupatlaScipyTwin(TwinSolver):
    """`ChandrupatlaScipyTwin` hands the interval to `scipy.optimize.elementwise.find_root`, which implements
    Chandrupatla's method, and returns ``xm`` after the evaluation at which `Chandrupatla` would stop.

    SciPy stops once the interval is narrower than ``xatol + xrtol * |xm|``, or once ``|f(xm)|`` is at most its
    function tolerances. The twin passes ``xatol = xtol`` and 0 for the other 3 tolerances, which gives the stopping
    criterion and the ``tl`` of `Chandrupatla`.

    SciPy calls the function with arrays; the twin evaluates each element through the `TwinFunction`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first point;
    - SciPy computes the interpolated ``t`` as the paper's equation 3, where `Chandrupatla` follows the BASIC listing's
      4 quotients, so the evaluated points can differ in their last bits.
    """

    name = "chandrupatla_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: TwinFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's find_root with ``xtol`` as its only nonzero tolerance."""

        def f_elementwise(x: np.ndarray) -> np.ndarray:
            return np.asarray([f(float(x_i)) for x_i in np.ravel(x)]).reshape(np.shape(x))

        tolerances = {"xatol": xtol, "xrtol": 0.0, "fatol": 0.0, "frtol": 0.0}
        scipy.optimize.elementwise.find_root(f_elementwise, (a, b), tolerances=tolerances)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``xm`` if `Chandrupatla` stops after the last of ``evaluations``, or ``None`` if it continues.

        As in `Chandrupatla`, ``xm`` is the interval bound with the smaller ``|f|``, and the newest point when both
        are equal.
        """
        x_newest, f_newest = evaluations[-1]
        if x_newest == interval.a:
            x_other, f_other = interval.b, interval.fb
        else:
            x_other, f_other = interval.a, interval.fa
        if abs(f_other) < abs(f_newest):
            xm, fm = x_other, f_other
        else:
            xm, fm = x_newest, f_newest
        if 0.5 * xtol / abs(x_other - x_newest) > 0.5 or fm == 0.0:
            return xm
        else:
            return None
