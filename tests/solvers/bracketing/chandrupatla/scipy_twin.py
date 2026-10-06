"""`ChandrupatlaScipyTwin` runs `scipy.optimize.elementwise.find_root` as a `Solver`, so `Chandrupatla` can be tested
against it."""

import numpy as np
import scipy.optimize.elementwise

from sunnbear.solvers import Interval
from tests.solvers.twins import StoppingWrappedFunction, TwinSolver


class ChandrupatlaScipyTwin(TwinSolver):
    """`ChandrupatlaScipyTwin` hands the interval to `scipy.optimize.elementwise.find_root`, which implements
    Chandrupatla's method. At the evaluation where `Chandrupatla` would stop, the twin returns ``xm``, the interval
    bound with the smaller ``|f|``.

    SciPy stops once the interval is narrower than ``xatol + xrtol * |xm|``, or once ``|f(xm)|`` is at most the
    tolerance that it computes from ``fatol`` and ``frtol``.

    The twin passes ``xatol = xtol`` and 0 for ``xrtol``, ``fatol`` and ``frtol``, which makes SciPy stop where
    `Chandrupatla` stops and keep each new point as far inside the interval as `Chandrupatla` does.

    SciPy calls the function with arrays; the twin evaluates each element through the `StoppingWrappedFunction`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first point;
    - SciPy computes the interpolated ``t`` with the paper's equation 3, while `Chandrupatla` computes it from the 4
      quotients of the BASIC listing, so the evaluated points can differ in their last bits.
    """

    name = "chandrupatla_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's find_root with ``xtol`` as its only nonzero tolerance."""
        tolerances = {"xatol": xtol, "xrtol": 0.0, "fatol": 0.0, "frtol": 0.0}
        # otypes stops np.vectorize from calling f once more to find the output type, an evaluation that
        # `Chandrupatla` does not make.
        scipy.optimize.elementwise.find_root(np.vectorize(f, otypes=[float]), (a, b), tolerances=tolerances)

    def _root_if_sunnbear_solver_stops(
        self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float
    ) -> float | None:
        """Return ``xm`` if `Chandrupatla` stops after the last of ``evaluations``, or ``None`` if it continues.

        As in `Chandrupatla`, ``xm`` is the bound that `_get_bounds_best_estimate_first` puts first.
        """
        (xm, fm), (x_other, _) = self._get_bounds_best_estimate_first(interval)
        if 0.5 * xtol / abs(x_other - xm) > 0.5 or fm == 0.0:
            return xm
        else:
            return None
