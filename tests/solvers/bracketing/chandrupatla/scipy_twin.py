"""`ChandrupatlaScipyTwin` runs `scipy.optimize.elementwise.find_root` as a `Solver`, so `Chandrupatla` can be tested
against it."""

import numpy as np
import scipy.optimize.elementwise

from tests.solvers.twins import StoppingWrappedFunction, TwinSolver


class ChandrupatlaScipyTwin(TwinSolver):
    """`ChandrupatlaScipyTwin` hands the interval to `scipy.optimize.elementwise.find_root`, which implements
    Chandrupatla's method, and stops it by the default of `TwinSolver`, the stopping criterion that `Chandrupatla`
    shares with `BracketingSolver`.

    SciPy's tolerance is ``tol = xatol + xrtol*|xm|``, where ``xm`` is the interval bound with the smaller ``|f|``.
    SciPy keeps each new x-value at least ``0.5*tol`` inside the interval, and stops once the interval is narrower
    than ``tol``, or once ``|f(xm)|`` is at most the tolerance that it computes from ``fatol`` and ``frtol``.

    The twin passes ``xatol = 2*xtol`` and 0 for ``xrtol``, ``fatol`` and ``frtol``, so that SciPy keeps each new
    x-value as far inside the interval as `Chandrupatla` does, ``xtol``. SciPy then stops only where the shared
    stopping criterion holds too: once the interval is narrower than ``2*xtol``, or once ``f(xm)`` is 0. The one
    exception is SciPy's check before its first x-value, which `Chandrupatla` does not make: on an initial interval
    narrower than ``2*xtol``, SciPy stops before it evaluates anything. No compared test case has such an interval.

    SciPy calls the function with arrays; the twin evaluates each element through the `StoppingWrappedFunction`.

    The twin deviates from exact agreement in these declared ways:

    - SciPy evaluates both interval bounds again before its first x-value;
    - SciPy computes the interpolated ``t`` with the paper's equation 3, while `Chandrupatla` computes it from the 4
      quotients of the BASIC listing, so the evaluated x-values can differ in their last bits.
    """

    name = "chandrupatla_scipy_twin"
    version = 1
    n_reevaluated_bounds = 2

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run SciPy's find_root with ``2*xtol`` as its only nonzero tolerance."""
        tolerances = {"xatol": 2.0 * xtol, "xrtol": 0.0, "fatol": 0.0, "frtol": 0.0}
        # otypes stops np.vectorize from calling f once more to find the output type, an evaluation that
        # `Chandrupatla` does not make.
        scipy.optimize.elementwise.find_root(np.vectorize(f, otypes=[float]), (a, b), tolerances=tolerances)
